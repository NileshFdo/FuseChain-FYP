"""
FuseChain Backend Configuration
"""

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "ml_pipeline" / "data" / "processed" / "final"

# Model paths
MODEL_PATH = MODELS_DIR / "xgboost_model.joblib"

# Data paths
TRAIN_DATA_PATH = DATA_DIR / "final_train_data.parquet"
OFFCHAIN_DATA_PATH = DATA_DIR / "offchain_daily.parquet"

# Feature columns
ONCHAIN_FEATURES = [
    'normal_total_cnt',
    'uniq_peers_cnt',
    'burst_max_tx_5m',
    'normal_sent_cnt',
]

REDDIT_FEATURES = [
    'reddit_fraud_mention_ratio',
    'reddit_total_activity',
    'reddit_avg_sentiment',
]

MARKET_FEATURES = [
    'eth_volatility_7d',
    'eth_daily_return',
    'eth_intraday_volatility',
]

# Off-chain features (Reddit + Market)
OFFCHAIN_FEATURES = REDDIT_FEATURES + MARKET_FEATURES

ALL_FEATURES = ONCHAIN_FEATURES + OFFCHAIN_FEATURES

# API Settings
API_PREFIX = "/api"
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # Create React App default
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
