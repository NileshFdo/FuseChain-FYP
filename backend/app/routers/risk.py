from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd
import numpy as np

from app.services import data_service, ml_service
from app.config import (
    ONCHAIN_FEATURES, OFFCHAIN_FEATURES, REDDIT_FEATURES, MARKET_FEATURES,
    LOCAL_SAMPLE_DIR
)

router = APIRouter(prefix="/risk", tags=["risk-assessment"])


class RiskResult(BaseModel):
    wallet_address: str
    risk_score: float
    is_flagged: bool
    top_reason: str
    detailed_reasons: List[str] = []
    on_chain_features: Dict[str, float]
    reddit_features: Dict[str, float]
    market_features: Dict[str, float]


class DateScanResponse(BaseModel):
    scan_date: str
    total_wallets: int
    flagged_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    max_probability: float
    avg_probability: float
    results: List[RiskResult]


class HistoryStats(BaseModel):
    days_analyzed: int
    avg_risk_score: float
    avg_daily_tx: float
    avg_sent_eth: float

class HistoryPoint(BaseModel):
    date: str
    risk_score: float
    is_flagged: bool
    top_reason: str

class WalletHistoryResponse(BaseModel):
    address: str
    history: List[HistoryPoint]
    stats: HistoryStats


class FeatureAnalysis(BaseModel):
    feature: str
    value: float
    baseline: float
    change_pct: float
    z_score: float
    explanation: str = ""


class AddressAnalysisResponse(BaseModel):
    wallet_address: str
    date: str
    risk_score: float
    is_flagged: bool
    top_reason: str
    history_comparison: List[str]
    feature_analysis: List[FeatureAnalysis]
    on_chain_features: Dict[str, float]
    reddit_features: Dict[str, float]
    market_features: Dict[str, float]
    has_history: bool


class ValidationMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int


class BatchResultItem(BaseModel):
    wallet_address: str
    risk_score: float
    is_flagged: bool
    top_reason: str
    on_chain_features: Dict[str, float]
    reddit_features: Dict[str, float]
    market_features: Dict[str, float]
    ground_truth: Optional[bool] = None
    is_correct: Optional[bool] = None


class BatchAnalysisResponse(BaseModel):
    analysis_date: str
    total_addresses: int
    flagged_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    results: List[BatchResultItem]
    has_validation: bool = False
    validation: Optional[ValidationMetrics] = None


@router.get("/scan-date", response_model=DateScanResponse)
async def scan_date(
    date: str,
    limit: Optional[int] = 100,
    only_anomalous: bool = False,
    threshold: float = 0.5
):
    train_data = data_service.train_data
    date_data = train_data[train_data['day'] == date].copy()
    
    if len(date_data) == 0:
        raise HTTPException(status_code=404, detail=f"No data found for date {date}")
    
    _, probabilities = ml_service.predict(date_data)
    
    results = []
    all_probs = list(probabilities)
    
    for idx, (_, row) in enumerate(date_data.iterrows()):
        prob = float(probabilities[idx])
        is_flagged = prob >= threshold
        
        if only_anomalous and not is_flagged:
            continue
        
        top_reason = "Normal activity"
        if is_flagged:
            contribs = ml_service.get_feature_contributions(row)
            all_contrib = {**contribs['on_chain'], **contribs['off_chain']}
            if all_contrib:
                pos_contrib = {k: v for k, v in all_contrib.items() if v > 0}
                if pos_contrib:
                    top_feature = max(pos_contrib.items(), key=lambda x: x[1])[0]
                    top_reason = f"High {format_feature_name(top_feature)}"
        
        results.append(RiskResult(
            wallet_address=row['address'],
            risk_score=round(prob * 100, 1),
            is_flagged=is_flagged,
            top_reason=top_reason,
            on_chain_features={col: float(row[col]) for col in ONCHAIN_FEATURES},
            reddit_features={col: float(row[col]) for col in REDDIT_FEATURES},
            market_features={col: float(row[col]) for col in MARKET_FEATURES}
        ))
    
    results.sort(key=lambda x: x.risk_score, reverse=True)
    
    if limit:
        results = results[:limit]
    
    return DateScanResponse(
        scan_date=date,
        total_wallets=len(date_data),
        flagged_count=sum(1 for p in all_probs if p >= threshold),
        high_risk_count=sum(1 for p in all_probs if p >= 0.75),
        medium_risk_count=sum(1 for p in all_probs if 0.5 <= p < 0.75),
        low_risk_count=sum(1 for p in all_probs if p < 0.5),
        max_probability=round(max(all_probs) * 100, 1),
        avg_probability=round(np.mean(all_probs) * 100, 1),
        results=results
    )


@router.get("/wallet-history/{address}", response_model=WalletHistoryResponse)
async def get_wallet_history(address: str):
    address = address.lower()
    train_data = data_service.train_data
    
    addr_data = train_data[train_data['address'] == address].copy()
    
    if len(addr_data) == 0:
        raise HTTPException(status_code=404, detail=f"No history found for address {address}")
    
    addr_data = addr_data.sort_values('day')
    _, probabilities = ml_service.predict(addr_data)
    
    history = []
    for idx, (_, row) in enumerate(addr_data.iterrows()):
        prob = float(probabilities[idx])
        is_flagged = prob >= 0.5
        
        top_reason = "Normal"
        if is_flagged:
            contribs = ml_service.get_feature_contributions(row)
            all_contrib = {**contribs['on_chain'], **contribs['off_chain']}
            if all_contrib:
                pos_contrib = {k: v for k, v in all_contrib.items() if v > 0}
                if pos_contrib:
                    top_feature = max(pos_contrib.items(), key=lambda x: x[1])[0]
                    top_reason = format_feature_name(top_feature)
        
        history.append(HistoryPoint(
            date=str(row['day']),
            risk_score=round(prob * 100, 1),
            is_flagged=is_flagged,
            top_reason=top_reason
        ))
    
    avg_score = np.mean([h.risk_score for h in history])
    avg_tx = addr_data['normal_total_cnt'].mean() if 'normal_total_cnt' in addr_data.columns else 0
    avg_sent = addr_data['normal_sent_cnt'].mean() if 'normal_sent_cnt' in addr_data.columns else 0
    
    return WalletHistoryResponse(
        address=address,
        history=history,
        stats=HistoryStats(
            days_analyzed=len(history),
            avg_risk_score=round(avg_score, 1),
            avg_daily_tx=round(avg_tx, 1),
            avg_sent_eth=round(avg_sent, 2)
        )
    )


@router.get("/analyze-address", response_model=AddressAnalysisResponse)
async def analyze_address(address: str, date: str):
    address = address.lower()
    train_data = data_service.train_data
    
    row_data = train_data[(train_data['address'] == address) & (train_data['day'] == date)]
    
    if len(row_data) == 0:
        raise HTTPException(status_code=404, detail=f"No data found for address {address} on {date}")
    
    row = row_data.iloc[0]
    
    _, prob = ml_service.predict(row_data)
    prob = float(prob[0])
    is_flagged = prob >= 0.5
    
    history_data = train_data[train_data['address'] == address]
    has_history = len(history_data) > 1
    
    feature_analysis = []
    history_comparison = []
    
    for feat in ONCHAIN_FEATURES + OFFCHAIN_FEATURES:
        val = float(row[feat])
        
        if has_history:
            avg = float(history_data[feat].mean())
            std = float(history_data[feat].std()) if len(history_data) > 1 else 1.0
            z = (val - avg) / std if std > 0 else 0
            pct = ((val - avg) / avg * 100) if avg != 0 else 0
        else:
            avg = float(train_data[feat].mean())
            std = float(train_data[feat].std())
            z = (val - avg) / std if std > 0 else 0
            pct = ((val - avg) / avg * 100) if avg != 0 else 0
        
        explanation = generate_explanation(feat, val, avg, pct, abs(z)) if abs(z) > 1 else ""
        
        feature_analysis.append(FeatureAnalysis(
            feature=format_feature_name(feat),
            value=round(val, 2),
            baseline=round(avg, 2),
            change_pct=round(pct, 1),
            z_score=round(z, 2),
            explanation=explanation
        ))
        
        if abs(z) > 2:
            direction = "above" if z > 0 else "below"
            history_comparison.append(f"{format_feature_name(feat)} is {abs(pct):.0f}% {direction} baseline")
    
    top_reason = "Normal activity"
    if is_flagged:
        contribs = ml_service.get_feature_contributions(row)
        all_contrib = {**contribs['on_chain'], **contribs['off_chain']}
        if all_contrib:
            pos_contrib = {k: v for k, v in all_contrib.items() if v > 0}
            if pos_contrib:
                top_feature = max(pos_contrib.items(), key=lambda x: x[1])[0]
                top_reason = f"High {format_feature_name(top_feature)}"
    
    return AddressAnalysisResponse(
        wallet_address=address,
        date=date,
        risk_score=round(prob * 100, 1),
        is_flagged=is_flagged,
        top_reason=top_reason,
        history_comparison=history_comparison,
        feature_analysis=feature_analysis,
        on_chain_features={col: float(row[col]) for col in ONCHAIN_FEATURES},
        reddit_features={col: float(row[col]) for col in REDDIT_FEATURES},
        market_features={col: float(row[col]) for col in MARKET_FEATURES},
        has_history=has_history
    )


@router.get("/available-dates")
async def get_available_dates():
    train_data = data_service.train_data
    dates = sorted(train_data['day'].unique(), reverse=True)
    return {"dates": [str(d) for d in dates]}


@router.post("/analyze-batch", response_model=BatchAnalysisResponse)
async def analyze_batch(file: UploadFile = File(...), threshold: float = 0.5):
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        df = pd.read_csv(pd.io.common.StringIO(content_str))
        df.columns = df.columns.str.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")
    
    if 'address' not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must have 'address' column")
    
    df['address'] = df['address'].str.lower()
    
    if 'date' in df.columns:
        analysis_date = str(df['date'].iloc[0])
    else:
        analysis_date = "unknown"
    
    for col in ONCHAIN_FEATURES:
        if col not in df.columns:
            df[col] = 0
    
    offchain_df = data_service.offchain_data
    date_match = offchain_df[offchain_df['day'] == analysis_date]
    
    if len(date_match) > 0:
        offchain_values = {col: float(date_match[col].iloc[0]) for col in OFFCHAIN_FEATURES}
    else:
        offchain_values = {col: float(offchain_df[col].mean()) for col in OFFCHAIN_FEATURES}
    
    for col in OFFCHAIN_FEATURES:
        df[col] = offchain_values[col]
    
    _, probabilities = ml_service.predict(df)
    
    has_ground_truth = 'Class' in df.columns
    ground_truth_map = {}
    if has_ground_truth:
        ground_truth_map = dict(zip(df['address'], df['Class'].astype(int) == 1))
    
    results = []
    all_scores = []
    TP, TN, FP, FN = 0, 0, 0, 0
    
    for idx, row in df.iterrows():
        prob = float(probabilities[idx])
        all_scores.append(prob)
        is_flagged = prob >= threshold
        address = row['address']
        
        top_reason = "Normal activity"
        if is_flagged:
            contribs = ml_service.get_feature_contributions(row)
            all_contrib = {**contribs['on_chain'], **contribs['off_chain']}
            if all_contrib:
                pos_contrib = {k: v for k, v in all_contrib.items() if v > 0}
                if pos_contrib:
                    top_feature = max(pos_contrib.items(), key=lambda x: x[1])[0]
                    top_reason = f"High {format_feature_name(top_feature)}"
        
        gt = ground_truth_map.get(address)
        is_correct = None
        
        if gt is not None:
            is_correct = (is_flagged == gt)
            if is_flagged and gt:
                TP += 1
            elif not is_flagged and not gt:
                TN += 1
            elif is_flagged and not gt:
                FP += 1
            else:
                FN += 1
        
        results.append(BatchResultItem(
            wallet_address=address,
            risk_score=round(prob * 100, 1),
            is_flagged=is_flagged,
            top_reason=top_reason,
            on_chain_features={col: float(row[col]) for col in ONCHAIN_FEATURES},
            reddit_features={col: offchain_values.get(col, 0) for col in REDDIT_FEATURES},
            market_features={col: offchain_values.get(col, 0) for col in MARKET_FEATURES},
            ground_truth=gt,
            is_correct=is_correct
        ))
    
    results.sort(key=lambda x: x.risk_score, reverse=True)
    
    validation = None
    if has_ground_truth and (TP + TN + FP + FN) > 0:
        total = TP + TN + FP + FN
        accuracy = (TP + TN) / total
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        validation = ValidationMetrics(
            accuracy=round(accuracy, 3),
            precision=round(precision, 3),
            recall=round(recall, 3),
            f1_score=round(f1, 3),
            true_positives=TP,
            true_negatives=TN,
            false_positives=FP,
            false_negatives=FN
        )
    
    return BatchAnalysisResponse(
        analysis_date=analysis_date,
        total_addresses=len(df),
        flagged_count=sum(1 for p in all_scores if p >= threshold),
        high_risk_count=sum(1 for p in all_scores if p >= 0.75),
        medium_risk_count=sum(1 for p in all_scores if 0.5 <= p < 0.75),
        low_risk_count=sum(1 for p in all_scores if p < 0.5),
        results=results,
        has_validation=has_ground_truth,
        validation=validation
    )


@router.get("/sample-files")
async def list_sample_files():
    if not LOCAL_SAMPLE_DIR.exists():
        return {"labeled": [], "unlabeled": []}
    
    labeled = []
    unlabeled = []
    
    for f in LOCAL_SAMPLE_DIR.glob("labeled_*.csv"):
        df = pd.read_csv(f)
        date_str = f.stem.replace("labeled_", "").replace("_", "-")
        labeled.append({
            "name": f.name,
            "addresses": len(df),
            "date": date_str,
            "has_labels": True
        })
    
    for f in LOCAL_SAMPLE_DIR.glob("unlabeled_*.csv"):
        df = pd.read_csv(f)
        date_str = f.stem.replace("unlabeled_", "").replace("_", "-")
        unlabeled.append({
            "name": f.name,
            "addresses": len(df),
            "date": date_str,
            "has_labels": False
        })
    
    return {
        "labeled": sorted(labeled, key=lambda x: x["date"]),
        "unlabeled": sorted(unlabeled, key=lambda x: x["date"])
    }


@router.get("/sample-files/{filename}")
async def download_sample_file(filename: str):
    from app.config import get_sample_file_path
    
    try:
        file_path = get_sample_file_path(filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    
    return FileResponse(path=file_path, filename=filename, media_type="text/csv")


def format_feature_name(name):
    names = {
        'normal_total_cnt': 'Tx Count',
        'uniq_peers_cnt': 'Unique Peers',
        'burst_max_tx_5m': 'Burst (5m)',
        'normal_sent_cnt': 'Sent Tx',
        'reddit_fraud_mention_ratio': 'Fraud Ratio',
        'reddit_total_activity': 'Social Activity',
        'reddit_avg_sentiment': 'Sentiment',
        'eth_volatility_7d': 'Vol (7d)',
        'eth_daily_return': 'Daily Return',
        'eth_intraday_volatility': 'Intraday Vol'
    }
    return names.get(name, name.replace('_', ' ').title())


def generate_explanation(feature, val, avg, pct, z):
    if z < 0.5:
        return ""
    
    if feature == 'normal_total_cnt':
        return f"Extreme spike in transaction frequency. {int(val)} transactions vs typical {avg:.1f} ({pct:.0f}% increase)."
    elif feature == 'normal_sent_cnt':
        return f"Abnormal outgoing activity. Sent {int(val)} transactions vs baseline {avg:.1f}."
    elif feature == 'uniq_peers_cnt':
        return f"Contacted {int(val)} unique addresses vs normal {avg:.1f}. Pattern consistent with distribution schemes."
    elif feature == 'eth_volatility_7d':
        return f"Activity coincides with market volatility ({val:.1f})."
    elif feature == 'reddit_avg_sentiment':
        return f"Negative sentiment detected in crypto communities."
    
    return f"Significant deviation in {format_feature_name(feature)} ({pct:.0f}% above baseline)."
