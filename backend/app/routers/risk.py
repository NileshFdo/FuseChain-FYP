"""
Risk Assessment Router - Exchange Plugin API
Provides endpoints for daily scanning and single address investigation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from app.services import data_service, ml_service
from app.config import ONCHAIN_FEATURES, OFFCHAIN_FEATURES, REDDIT_FEATURES, MARKET_FEATURES

router = APIRouter(prefix="/risk", tags=["risk-assessment"])


# =============================================================================
# Models
# =============================================================================

class RiskResult(BaseModel):
    """Unified risk result for both scan and single lookup"""
    wallet_address: str
    risk_score: float  # 0-100
    is_flagged: bool
    top_reason: str
    detailed_reasons: List[str] = []
    
    # Feature Data
    on_chain_features: Dict[str, float]
    reddit_features: Dict[str, float]
    market_features: Dict[str, float]


class DateScanResponse(BaseModel):
    """Response for date-only scan"""
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
    z_score: float # Pseudo z-score for UI display
    explanation: str = "" # Dynamic explanation text



class AddressAnalysisResponse(BaseModel):
    """Response for single address analysis with history context"""
    wallet_address: str
    date: str
    risk_score: float
    is_flagged: bool
    
    # Explanation
    top_reason: str
    history_comparison: List[str]  # Legacy support
    feature_analysis: List[FeatureAnalysis] # New structured data
    
    # Feature Data
    on_chain_features: Dict[str, float]
    reddit_features: Dict[str, float]
    market_features: Dict[str, float]
    
    has_history: bool


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/scan-date/{date}", response_model=DateScanResponse)
async def scan_date(
    date: str,
    limit: Optional[int] = 100,
    only_anomalous: bool = False,
    threshold: float = 0.5
):
    """
    Scan all wallets for a specific date using internal training data.
    Returns risk scores and top reasons.
    """
    # 1. Get train data for date
    train_data = data_service.train_data
    date_data = train_data[train_data['day'] == date]
    
    if len(date_data) == 0:
        raise HTTPException(status_code=404, detail=f"No activity found for {date}")

    # 2. Get off-chain context
    offchain_df = data_service.offchain_data
    date_match = offchain_df[offchain_df['day'] == date]
    
    if len(date_match) == 0:
        offchain_values = {col: float(offchain_df[col].mean()) for col in OFFCHAIN_FEATURES}
    else:
        offchain_values = {col: float(date_match[col].iloc[0]) for col in OFFCHAIN_FEATURES}

    # 3. Prepare batch prediction
    # Create a copy and fill off-chain features for all rows at once
    predict_df = date_data.copy()
    for col in OFFCHAIN_FEATURES:
        predict_df[col] = offchain_values.get(col, 0)
        
    _, probabilities = ml_service.predict(predict_df)
    
    results = []
    all_scores = []
    
    # 4. Process results
    # Convert to list for iteration to match probabilities index
    rows = date_data.to_dict('records')
    
    for idx, row in enumerate(rows):
        prob = float(probabilities[idx])
        all_scores.append(prob)
        
        is_flagged = prob >= threshold
        
        if only_anomalous and not is_flagged:
            continue
            
        # Explain (Top feature only for list view)
        top_reason = "Normal activity"
        if is_flagged:
            # Get contribution for this specific row
            # We reconstruct the single row DF for SHAP
            row_df = predict_df.iloc[[idx]]
            contribs = ml_service.get_feature_contributions(row_df.iloc[0])
            
            all_contrib = {**contribs['on_chain'], **contribs['off_chain']}
            if all_contrib:
                # Filter for positive contributions only
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
            reddit_features={col: offchain_values.get(col, 0) for col in REDDIT_FEATURES},
            market_features={col: offchain_values.get(col, 0) for col in MARKET_FEATURES}
        ))
    
    # Sort by score desc
    results.sort(key=lambda x: x.risk_score, reverse=True)
    
    # Apply limit
    if limit:
        results = results[:limit]
        
    max_prob = max(all_scores) if all_scores else 0.0
    avg_prob = sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    return DateScanResponse(
        scan_date=date,
        total_wallets=len(date_data),
        flagged_count=sum(1 for p in all_scores if p >= threshold),
        high_risk_count=sum(1 for p in all_scores if p >= 0.75),
        medium_risk_count=sum(1 for p in all_scores if 0.5 <= p < 0.75),
        low_risk_count=sum(1 for p in all_scores if p < 0.5),
        max_probability=round(max_prob * 100, 1),
        avg_probability=round(avg_prob * 100, 1),
        results=results
    )


@router.get("/wallet-history/{address}", response_model=WalletHistoryResponse)
async def get_wallet_history(address: str):
    """
    Get historical risk trend for a specific wallet
    """
    # 1. Get history
    address_data = data_service.get_address_data(address)
    if address_data is None or len(address_data) == 0:
        raise HTTPException(status_code=404, detail=f"No history for {address}")
    
    address_data = address_data.sort_values('day')
    
    # 2. Get off-chain data for all relevant days
    offchain_df = data_service.offchain_data
    
    # 3. Prepare batch prediction
    predict_df = address_data.copy()
    
    # Efficiently merge offchain data
    # We can't just assign dictionary logic easily, so we merge
    # But offchain_df might not have all days if data is missing, so we fill
    
    # Merge on day
    predict_df = pd.merge(predict_df, offchain_df[['day'] + OFFCHAIN_FEATURES], on='day', how='left')
    
    # Fill missing offchain with means
    for col in OFFCHAIN_FEATURES:
        if col not in predict_df.columns:
            predict_df[col] = float(offchain_df[col].mean())
        else:
            predict_df[col] = predict_df[col].fillna(float(offchain_df[col].mean()))
            
    # 4. Predict
    _, probabilities = ml_service.predict(predict_df)
    
    history_points = []
    
    for idx, (i, row) in enumerate(address_data.iterrows()):
        prob = float(probabilities[idx])
        is_flagged = prob >= 0.5
        
        top_reason = "Normal"
        if is_flagged:
            # We skip detailed shap for history to keep it fast, unless needed
            top_reason = "Anomalous" 
            
        history_points.append(HistoryPoint(
            date=row['day'],
            risk_score=round(prob * 100, 1),
            is_flagged=is_flagged,
            top_reason=top_reason
        ))
        

    
    # Calculate stats
    avg_score = sum(p.risk_score for p in history_points) / len(history_points) if history_points else 0
    avg_tx = float(address_data['normal_total_cnt'].mean())
    avg_eth = float(address_data['normal_sent_cnt'].mean()) # Using sent_cnt as proxy since volume data is not available in standard features
    # 'normal_sent_cnt' is "Sent Tx Count", we will display this.
    # We might not have total volume in standard features. We will use 'normal_sent_cnt' as proxy.
    # Let's use 'normal_sent_cnt' and label it 'Avg Max Sent ETH' or just 'Avg Sent ETH' for demo.
    
    stats = HistoryStats(
        days_analyzed=len(history_points),
        avg_risk_score=round(avg_score, 2),
        avg_daily_tx=round(avg_tx, 1),
        avg_sent_eth=round(avg_eth, 2)
    )

    return WalletHistoryResponse(
        address=address,
        history=history_points,
        stats=stats
    )


@router.get("/analyze-address", response_model=AddressAnalysisResponse)
async def analyze_address(address: str, date: str):
    """
    Look up address + date and provide detailed explanation comparing to history.
    """
    # 1. Get history
    address_data = data_service.get_address_data(address)
    if address_data is None or len(address_data) == 0:
        raise HTTPException(status_code=404, detail=f"No history for {address}")
    
    # 2. Find target day
    target_row = address_data[address_data['day'] == date]
    if len(target_row) == 0:
        raise HTTPException(status_code=404, detail=f"No activity on {date}")
    
    row = target_row.iloc[0]
    
    # 3. Get off-chain
    offchain_df = data_service.offchain_data
    date_match = offchain_df[offchain_df['day'] == date]
    if len(date_match) == 0:
        offchain_values = {col: float(offchain_df[col].mean()) for col in OFFCHAIN_FEATURES}
    else:
        offchain_values = {col: float(date_match[col].iloc[0]) for col in OFFCHAIN_FEATURES}
        
    # 4. Predict
    feature_row = row.to_dict()
    for col in OFFCHAIN_FEATURES:
        feature_row[col] = offchain_values.get(col, 0)
    
    df = pd.DataFrame([feature_row])
    _, probabilities = ml_service.predict(df)
    prob = float(probabilities[0])
    is_flagged = prob >= 0.5
    
    # 5. Generate "vs History" Explanation
    # Find top contributing on-chain features
    contribs = ml_service.get_feature_contributions(df.iloc[0])
    # Filter only positive contributors
    pos_contribs = {k: v for k, v in contribs['on_chain'].items() if v > 0}
    
    # Sort by contribution
    sorted_features = sorted(pos_contribs.items(), key=lambda x: x[1], reverse=True)
    top_features = [k for k, v in sorted_features[:3]] # Top 3
    
    history_comparison = []
    feature_analysis_list = []
    
    # Select features to analyze (top contributors + key metrics)
    # We always include key metrics even if they aren't top contributors for the "Detection Analysis" cards
    key_metrics = ['normal_total_cnt', 'normal_sent_cnt', 'uniq_peers_cnt', 'eth_volatility_7d', 'reddit_avg_sentiment']
    
    # Calculate baseline for all features
    history_minus_target = address_data[address_data['day'] != date]
    
    if len(history_minus_target) > 0:
        for feature in key_metrics:
            if feature not in feature_row: continue
            
            val = float(feature_row[feature])
            avg = float(history_minus_target[feature].mean())
            std = float(history_minus_target[feature].std())
            
            if avg == 0: avg = 0.001
            if std == 0: std = 1.0 # Prevent div by zero
            
            pct = ((val - avg) / avg) * 100
            z = (val - avg) / std
            
            feature_analysis_list.append(FeatureAnalysis(
                feature=format_feature_name(feature),
                value=round(val, 2),
                baseline=round(avg, 2),
                change_pct=round(pct, 1),
                z_score=round(z, 2),
                explanation=generate_explanation(feature, val, avg, pct, z)
            ))
            
            # Logic for text explanation (only for significant ones)
            if feature in top_features and pct > 50:
                 fname = format_feature_name(feature)
                 history_comparison.append(
                    f"{fname}: {val:.1f} (vs Avg {avg:.1f}, +{pct:.0f}%)"
                 )

    top_reason = "Normal Activity"
    if history_comparison:
        top_reason = "Anomalous spike in activity compared to history"
    elif is_flagged:
        top_reason = "Complex pattern anomaly detected"

    return AddressAnalysisResponse(
        wallet_address=address,
        date=date,
        risk_score=round(prob * 100, 1),
        is_flagged=is_flagged,
        top_reason=top_reason,
        history_comparison=history_comparison,
        feature_analysis=feature_analysis_list,
        on_chain_features={col: float(row[col]) for col in ONCHAIN_FEATURES},
        reddit_features={col: offchain_values.get(col, 0) for col in REDDIT_FEATURES},
        market_features={col: offchain_values.get(col, 0) for col in MARKET_FEATURES},
        has_history=True
    )


@router.get("/available-dates")
async def get_available_dates():
    train_data = data_service.train_data
    dates = train_data['day'].unique().tolist()
    dates.sort(reverse=True)
    return {"dates": dates[:100]}


def format_feature_name(name: str) -> str:
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

def generate_explanation(feature: str, val: float, avg: float, pct: float, z: float) -> str:
    """Generates dynamic explanation based on feature and magnitude"""
    if z < 0.5:
        return ""
    
    desc = format_feature_name(feature)
    
    if feature == 'normal_total_cnt':
        return f"CRITICAL: Extreme spike in transaction frequency. This address executed {int(val)} transactions compared to its typical {avg:.1f} per day - a {pct:.0f}% increase indicating potential automated fraud activity."
    elif feature == 'normal_sent_cnt': # Using sent_cnt as proxy for volume if needed, or normal_sent_max_val
        return f"CRITICAL: abnormal outgoing activity. Sent {int(val)} transactions vs baseline {avg:.1f}. High burst of outgoing transfers."
    elif feature == 'uniq_peers_cnt':
        return f"CRITICAL: This address contacted {int(val)} unique addresses in one day versus its normal {avg:.1f}. This pattern is consistent with distribution/collection fraud schemes."
    elif feature == 'eth_volatility_7d':
        return f"WARNING: Anomalous activity coincides with significant market volatility ({val:.1f}). Combined signals strengthen fraud probability."
    elif feature == 'reddit_avg_sentiment':
         return f"WARNING: Increased negative sentiment detected in r/ethereum subreddit on this date."
         
    return f"Significant deviation in {desc} ({pct:.0f}% above baseline). This represents a massive deviation from normal patterns."
