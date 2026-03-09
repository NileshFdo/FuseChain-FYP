import os
import json
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

MODEL_FILENAME = "xgboost_address_model.joblib"
ADDRESS_DATA_FILENAME = "address_level_fused.parquet"
METADATA_FILENAME = "address_features_metadata.json"

LOCAL_MODEL_PATH = MODELS_DIR / MODEL_FILENAME
LOCAL_ADDRESS_DATA_PATH = DATA_DIR / ADDRESS_DATA_FILENAME
LOCAL_METADATA_PATH = MODELS_DIR / METADATA_FILENAME

LOCAL_SAMPLE_DIR = MODELS_DIR


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

def get_address_data_path():
    return get_path(LOCAL_ADDRESS_DATA_PATH, ADDRESS_DATA_FILENAME, HF_DATA_REPO_ID, repo_type=HF_DATA_REPO_TYPE)

def get_metadata_path():
    return get_path(LOCAL_METADATA_PATH, METADATA_FILENAME, HF_MODEL_REPO_ID, repo_type=HF_MODEL_REPO_TYPE)

def get_sample_file_path(filename):
    """Get path to a sample CSV, local-first with HuggingFace fallback."""
    local_path = LOCAL_SAMPLE_DIR / filename
    if local_path.exists():
        return local_path
    return get_path(local_path, filename, HF_MODEL_REPO_ID, repo_type=HF_MODEL_REPO_TYPE)


# ---------------------------------------------------------------------------
# Load feature lists dynamically from metadata JSON
# ---------------------------------------------------------------------------

def _load_feature_metadata():
    """Load feature groups from address_features_metadata.json."""
    meta_path = get_metadata_path()
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    return meta

def _auto_display_name(feature_name: str) -> str:
    """Convert a snake_case feature name to a human-readable display name."""
    # Remove common suffixes for cleaner names
    name = feature_name
    for prefix in ['market_', 'reddit_', 'twitter_']:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break

    # Convert snake_case to Title Case
    parts = name.replace('_', ' ').split()
    # Capitalize meaningful words
    result = []
    for p in parts:
        if p in ('eth', 'tx', '7d', '30d', '5m', 'cnt', 'std', 'avg'):
            result.append(p.upper())
        elif p == 'min':
            result.append('Min')
        else:
            result.append(p.capitalize())
    return ' '.join(result)


_meta = _load_feature_metadata()

ONCHAIN_FEATURES = _meta.get('onchain_features', [])
MARKET_FEATURES = _meta.get('market_features', [])
REDDIT_FEATURES = _meta.get('reddit_features', [])
TWITTER_FEATURES = _meta.get('twitter_features', [])

OFFCHAIN_FEATURES = MARKET_FEATURES + REDDIT_FEATURES + TWITTER_FEATURES
ALL_FEATURES = ONCHAIN_FEATURES + OFFCHAIN_FEATURES

print(f"Loaded features from metadata: {len(ALL_FEATURES)} total "
      f"({len(ONCHAIN_FEATURES)} on-chain, {len(MARKET_FEATURES)} market, "
      f"{len(REDDIT_FEATURES)} reddit, {len(TWITTER_FEATURES)} twitter)")

API_PREFIX = ""
CORS_ORIGINS = ["*"]

# Auto-generate display names from feature names
FEATURE_DISPLAY_NAMES = {feat: _auto_display_name(feat) for feat in ALL_FEATURES}
