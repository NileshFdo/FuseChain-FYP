from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from app.services.data_service import data_service
from app.services.ml_service import ml_service
from app.config import (
    ONCHAIN_FEATURES, MARKET_FEATURES, REDDIT_FEATURES, TWITTER_FEATURES,
    FEATURE_DISPLAY_NAMES,
)

router = APIRouter(prefix="/risk", tags=["risk-assessment"])


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class ShapFeature(BaseModel):
    """
    Schema for a single feature's SHAP contribution
    """
    feature: str
    display_name: str
    shap_value: float
    modality: str
    value: Optional[float] = None


class RiskResult(BaseModel):
    """
    schema returned for a single address analysis
    Contains the prediction, probability, human-readable narrative, 
    and detailed feature values for UI display
    """
    wallet_address: str
    risk_score: float
    is_flagged: bool
    verdict: str
    narrative: str = ""
    top_reasons: List[str] = []
    top_shap_features: List[ShapFeature] = []
    on_chain_features: Dict[str, float] = {}
    market_features: Dict[str, float] = {}
    reddit_features: Dict[str, float] = {}
    twitter_features: Dict[str, float] = {}
    shap_contributions: Dict[str, float] = {}


class BatchResultItem(BaseModel):
    wallet_address: str
    risk_score: float
    is_flagged: bool
    verdict: str
    top_reasons: List[str] = []
    ground_truth: Optional[bool] = None
    is_correct: Optional[bool] = None


class ValidationMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int


class BatchAnalysisResponse(BaseModel):
    total_addresses: int
    flagged_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    results: List[BatchResultItem]
    has_validation: bool = False
    validation: Optional[ValidationMetrics] = None


# Endpoints

@router.get("/analyze/{address}", response_model=RiskResult)
async def analyze_address(address: str):
    """
    Analyze a single Ethereum address and return scam risk score,
    verdict, SHAP-based top reasons, and feature breakdowns
    """
    # Lookup the address profile
    profile = data_service.get_address_profile(address)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Address {address} not found in dataset.")

    # Predict
    prediction, probability = ml_service.predict_single(profile)

    # SHAP explanations for transparency and UI
    contributions = ml_service.get_feature_contributions(profile)
    verdict = "Scam" if prediction == 1 else "Normal"
    top_reasons = ml_service.generate_top_reasons(contributions, profile=profile, n=5)
    narrative = ml_service.generate_narrative(contributions, profile, verdict, float(probability))
    top_shap = ml_service.get_top_shap_features(contributions, profile=profile, n=8)

    # Dictionary of raw feature values for the UI tables
    features = data_service.extract_features(profile)

    # Flatten the SHAP contributions to send to the frontend
    flat_shap = {}
    for group in contributions.values():
        flat_shap.update(group)

    return RiskResult(
        wallet_address=address,
        risk_score=round(float(probability), 4),
        is_flagged=bool(prediction == 1),
        verdict=verdict,
        narrative=narrative,
        top_reasons=top_reasons,
        top_shap_features=top_shap,
        on_chain_features=features['on_chain'],
        market_features=features['market'],
        reddit_features=features['reddit'],
        twitter_features=features['twitter'],
        shap_contributions=flat_shap,
    )


@router.post("/analyze-batch", response_model=BatchAnalysisResponse)
async def analyze_batch(file: UploadFile = File(...), threshold: float = 0.5):
    """
    Upload a CSV with address column
    Optionally include is_scam column for ground-truth validation
    """
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

    if 'address' not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain an 'address' column.")

    has_labels = 'is_scam' in df.columns

    results: List[BatchResultItem] = []
    tp = tn = fp = fn = 0

    for _, row in df.iterrows():
        addr = str(row['address']).strip()
        profile = data_service.get_address_profile(addr)

        if profile is None:
            continue

        # Make the prediction against the loaded XGBoost model
        prediction, probability = ml_service.predict_single(profile)
        is_flagged = float(probability) >= threshold
        
        # Generate SHAP explanations for this specific address
        contributions = ml_service.get_feature_contributions(profile)
        top_reasons = ml_service.generate_top_reasons(contributions)
        verdict = "Scam" if is_flagged else "Normal"

        ground_truth = None
        is_correct = None
        if has_labels:
            ground_truth = bool(int(row['is_scam']))
            is_correct = (is_flagged == ground_truth)
            if ground_truth and is_flagged:
                tp += 1
            elif not ground_truth and not is_flagged:
                tn += 1
            elif not ground_truth and is_flagged:
                fp += 1
            else:
                fn += 1

        results.append(BatchResultItem(
            wallet_address=addr,
            risk_score=round(float(probability), 4),
            is_flagged=is_flagged,
            verdict=verdict,
            top_reasons=top_reasons,
            ground_truth=ground_truth,
            is_correct=is_correct,
        ))

    # Categorize results for the frontend dashboard
    high = sum(1 for r in results if r.risk_score >= 0.75)
    medium = sum(1 for r in results if 0.4 <= r.risk_score < 0.75)
    low = sum(1 for r in results if r.risk_score < 0.4)

    validation = None
    # Calculate performance metrics only if ground-truth labels were provided
    if has_labels and (tp + tn + fp + fn) > 0:
        total = tp + tn + fp + fn
        validation = ValidationMetrics(
            accuracy=round((tp + tn) / total, 4),
            precision=round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0,
            recall=round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0,
            f1_score=round(2 * tp / (2 * tp + fp + fn), 4) if (2 * tp + fp + fn) > 0 else 0.0,
            true_positives=tp,
            true_negatives=tn,
            false_positives=fp,
            false_negatives=fn,
        )

    return BatchAnalysisResponse(
        total_addresses=len(results),
        flagged_count=sum(1 for r in results if r.is_flagged),
        high_risk_count=high,
        medium_risk_count=medium,
        low_risk_count=low,
        results=sorted(results, key=lambda r: r.risk_score, reverse=True),
        has_validation=has_labels,
        validation=validation,
    )


from fastapi.responses import FileResponse
import os

@router.get("/sample-files")
async def get_sample_files():
    """Returns available sample files for testing"""
    return {
        "labeled": [
            {
                "name": "demo_labeled_addresses.csv",
                "addresses": "20 test addresses (10 scam, 10 normal)"
            }
        ],
        "unlabeled": [
            {
                "name": "demo_unlabeled_addresses.csv",
                "addresses": "20 test addresses"
            }
        ]
    }

@router.get("/sample-files/{filename}")
async def download_sample_file(filename: str):
    """Download a specific sample file"""
    from app.config import get_sample_file_path

    try:
        file_path = get_sample_file_path(filename)
    except Exception:
        raise HTTPException(status_code=404, detail="Sample file not found")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample file not found")

    return FileResponse(path=str(file_path), filename=filename, media_type='text/csv')

