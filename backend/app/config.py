import os
from pathlib import Path

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    hf_hub_download = None

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "ml_pipeline" / "data" / "processed" / "final"

HF_MODEL_REPO_ID = "Nileshka/fusechain-model"
HF_DATA_REPO_ID = "Nileshka/fusechain-data"

HF_MODEL_REPO_TYPE = "model"
HF_DATA_REPO_TYPE = "dataset"

MODEL_FILENAME = "xgboost_model.joblib"
TRAIN_DATA_FILENAME = "final_train_data.parquet"
OFFCHAIN_DATA_FILENAME = "offchain_daily.parquet"

LOCAL_MODEL_PATH = MODELS_DIR / MODEL_FILENAME
LOCAL_TRAIN_DATA_PATH = DATA_DIR / TRAIN_DATA_FILENAME
LOCAL_OFFCHAIN_DATA_PATH = DATA_DIR / OFFCHAIN_DATA_FILENAME


def get_path(local_path, filename, repo_id, repo_type):
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


def get_model_path():
    return get_path(LOCAL_MODEL_PATH, MODEL_FILENAME, HF_MODEL_REPO_ID, repo_type=HF_MODEL_REPO_TYPE)

def get_train_data_path():
    return get_path(LOCAL_TRAIN_DATA_PATH, TRAIN_DATA_FILENAME, HF_DATA_REPO_ID, repo_type=HF_DATA_REPO_TYPE)

def get_offchain_data_path():
    return get_path(LOCAL_OFFCHAIN_DATA_PATH, OFFCHAIN_DATA_FILENAME, HF_DATA_REPO_ID, repo_type=HF_DATA_REPO_TYPE)


LOCAL_SAMPLE_DIR = BASE_DIR / "ml_pipeline" / "data" / "sample_batches"

SAMPLE_FILES = [
    "labeled_2018_08_01.csv",
    "labeled_2018_08_07.csv",
    "labeled_2018_08_20.csv",
    "labeled_2018_09_05.csv",
    "labeled_2018_09_15.csv",
    "unlabeled_2018_08_01.csv",
    "unlabeled_2018_08_07.csv",
    "unlabeled_2018_08_20.csv",
    "unlabeled_2018_09_05.csv",
    "unlabeled_2018_09_15.csv",
]


def get_sample_file_path(filename):
    local_path = LOCAL_SAMPLE_DIR / filename
    if local_path.exists():
        return local_path

    if hf_hub_download is None:
        raise FileNotFoundError(f"Sample file not found: {filename}")
    
    print(f"Downloading sample file {filename} from HuggingFace...")
    downloaded_path = hf_hub_download(
        repo_id=HF_DATA_REPO_ID,
        filename=f"sample_batches/{filename}",
        repo_type=HF_DATA_REPO_TYPE
    )
    return Path(downloaded_path)


def list_available_sample_files():
    if LOCAL_SAMPLE_DIR.exists():
        labeled = list(LOCAL_SAMPLE_DIR.glob("labeled_*.csv"))
        unlabeled = list(LOCAL_SAMPLE_DIR.glob("unlabeled_*.csv"))
        return labeled + unlabeled
    return SAMPLE_FILES


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

API_PREFIX = ""
CORS_ORIGINS = ["*"]

FEATURE_DISPLAY_NAMES = {
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
