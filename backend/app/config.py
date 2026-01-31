"""
FuseChain Backend Configuration
"""
import os
from pathlib import Path

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    hf_hub_download = None

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "ml_pipeline" / "data" / "processed" / "final"

# Hugging Face repo identifiers
HF_MODEL_REPO_ID = "Nileshka/fusechain-model"
HF_DATA_REPO_ID = "Nileshka/fusechain-data"

# Repo types
HF_MODEL_REPO_TYPE = "model"
HF_DATA_REPO_TYPE = "dataset"

# Define Filenames
MODEL_FILENAME = "xgboost_model.joblib"
TRAIN_DATA_FILENAME = "final_train_data.parquet"
OFFCHAIN_DATA_FILENAME = "offchain_daily.parquet"

# Local Paths
LOCAL_MODEL_PATH = MODELS_DIR / MODEL_FILENAME
LOCAL_TRAIN_DATA_PATH = DATA_DIR / TRAIN_DATA_FILENAME
LOCAL_OFFCHAIN_DATA_PATH = DATA_DIR / OFFCHAIN_DATA_FILENAME


def get_path(local_path: Path, filename: str, repo_id: str, repo_type: str) -> Path:
    """
    Resolve path: use local file if exists, else download from HF Hub.
    """
    if local_path.exists():
        print(f"Found local file: {local_path}")
        return local_path

    print(f"Local file not found: {local_path}")
    print(f"Downloading {filename} from Hugging Face Hub ({repo_id}, type={repo_type})...")

    if hf_hub_download is None:
        raise ImportError("huggingface_hub not installed. Cannot download artifacts.")

    downloaded_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        repo_type=repo_type
    )
    print(f"Downloaded to: {downloaded_path}")
    return Path(downloaded_path)


def get_model_path() -> Path:
    return get_path(LOCAL_MODEL_PATH, MODEL_FILENAME, HF_MODEL_REPO_ID, repo_type=HF_MODEL_REPO_TYPE)

def get_train_data_path() -> Path:
    return get_path(LOCAL_TRAIN_DATA_PATH, TRAIN_DATA_FILENAME, HF_DATA_REPO_ID, repo_type=HF_DATA_REPO_TYPE)

def get_offchain_data_path() -> Path:
    return get_path(LOCAL_OFFCHAIN_DATA_PATH, OFFCHAIN_DATA_FILENAME, HF_DATA_REPO_ID, repo_type=HF_DATA_REPO_TYPE)


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

OFFCHAIN_FEATURES = REDDIT_FEATURES + MARKET_FEATURES
ALL_FEATURES = ONCHAIN_FEATURES + OFFCHAIN_FEATURES

# API Settings
API_PREFIX = "/api"
CORS_ORIGINS = ["*"]
