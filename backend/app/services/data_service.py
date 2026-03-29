import pandas as pd
from typing import List, Optional, Dict

from app.config import (
    get_address_data_path,
    ONCHAIN_FEATURES, MARKET_FEATURES, REDDIT_FEATURES, TWITTER_FEATURES,
    ALL_FEATURES, FEATURE_DISPLAY_NAMES,
)


class DataService:
    """
    Singleton service for loading the parquet dataset
    load only once upon application startup
    """

    def __init__(self):
        self._address_data = None
        self._address_cache = None
        self._stats_cache = None

    def load_data(self):
        data_path = get_address_data_path()
        print(f"Loading address-level data from {data_path}...")
        self._address_data = pd.read_parquet(data_path)
        self._address_cache = self._address_data['address'].unique().tolist()
        print(f"Loaded {len(self._address_data):,} address profiles")

        # Pre-compute per-feature mean/std for narrative comparisons
        numeric_cols = [c for c in ALL_FEATURES if c in self._address_data.columns]
        self._stats_cache = {}
        for col in numeric_cols:
            series = self._address_data[col].dropna()
            self._stats_cache[col] = {
                'mean': float(series.mean()),
                'std': float(series.std()),
                'median': float(series.median()),
            }

    @property
    def address_data(self):
        if self._address_data is None:
            self.load_data()
        return self._address_data

    def get_feature_stats(self, feature: str):
        """Return pre-computed mean, std, median for a feature, or None"""
        if self._stats_cache is None:
            self.load_data()
        return self._stats_cache.get(feature)

    def get_address_profile(self, address: str) -> Optional[pd.Series]:
        """Return the single-row profile for the given address, or None"""
        mask = self.address_data['address'].str.lower() == address.lower()
        matches = self.address_data[mask]

        if len(matches) == 0:
            return None
        return matches.iloc[0]

    def address_exists(self, address: str) -> bool:
        if self._address_cache is None:
            self.load_data()
        return address.lower() in [a.lower() for a in self._address_cache]

    def extract_features(self, row: pd.Series) -> Dict[str, Dict[str, float]]:
        """
        Takes a single Pandas Series (address profile) and splits features
        into the four distinct modalities (On-chain, Market, Reddit, Twitter)
        """
        on_chain = {col: float(row.get(col, 0)) for col in ONCHAIN_FEATURES if col in row.index}
        market = {col: float(row.get(col, 0)) for col in MARKET_FEATURES if col in row.index}
        reddit = {col: float(row.get(col, 0)) for col in REDDIT_FEATURES if col in row.index}
        twitter = {col: float(row.get(col, 0)) for col in TWITTER_FEATURES if col in row.index}
        return {
            'on_chain': on_chain,
            'market': market,
            'reddit': reddit,
            'twitter': twitter,
        }


data_service = DataService()
