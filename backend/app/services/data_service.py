"""
Data Service - Handles loading and processing of datasets
"""

import pandas as pd
from typing import List, Optional, Dict
from pathlib import Path

from app.config import TRAIN_DATA_PATH, OFFCHAIN_DATA_PATH, ONCHAIN_FEATURES, OFFCHAIN_FEATURES


class DataService:
    """Service for loading and managing datasets"""
    
    def __init__(self):
        self._train_data: Optional[pd.DataFrame] = None
        self._offchain_data: Optional[pd.DataFrame] = None
        self._address_cache: Optional[List[str]] = None
    
    def load_data(self):
        """Load datasets on startup"""
        print(f"Loading training data from {TRAIN_DATA_PATH}...")
        self._train_data = pd.read_parquet(TRAIN_DATA_PATH)
        self._train_data['day'] = pd.to_datetime(self._train_data['day']).dt.strftime('%Y-%m-%d')
        print(f"Loaded {len(self._train_data):,} rows")
        
        print(f"Loading off-chain data from {OFFCHAIN_DATA_PATH}...")
        self._offchain_data = pd.read_parquet(OFFCHAIN_DATA_PATH)
        self._offchain_data['day'] = pd.to_datetime(self._offchain_data['day']).dt.strftime('%Y-%m-%d')
        print(f"Loaded {len(self._offchain_data):,} rows")
        
        # Cache unique addresses
        self._address_cache = self._train_data['address'].unique().tolist()
        print(f"Cached {len(self._address_cache):,} unique addresses")
    
    @property
    def train_data(self) -> pd.DataFrame:
        if self._train_data is None:
            self.load_data()
        return self._train_data
    
    @property
    def offchain_data(self) -> pd.DataFrame:
        if self._offchain_data is None:
            self.load_data()
        return self._offchain_data
    
    def get_addresses(self, search: Optional[str] = None, limit: int = 100) -> List[str]:
        """Get list of available addresses with optional search filter"""
        if self._address_cache is None:
            self.load_data()
        
        addresses = self._address_cache
        
        if search:
            search_lower = search.lower()
            addresses = [a for a in addresses if search_lower in a.lower()]
        
        return addresses[:limit]
    
    def get_address_data(self, address: str) -> Optional[pd.DataFrame]:
        """Get all data for a specific address"""
        mask = self.train_data['address'].str.lower() == address.lower()
        data = self.train_data[mask].copy()
        
        if len(data) == 0:
            return None
        
        return data.sort_values('day')
    
    def address_exists(self, address: str) -> bool:
        """Check if address exists in dataset"""
        if self._address_cache is None:
            self.load_data()
        return address.lower() in [a.lower() for a in self._address_cache]
    
    def merge_with_offchain(self, onchain_df: pd.DataFrame) -> pd.DataFrame:
        """Merge on-chain data with off-chain features by date"""
        # Ensure day columns are in the same format
        onchain_df = onchain_df.copy()
        onchain_df['day'] = pd.to_datetime(onchain_df['day']).dt.strftime('%Y-%m-%d')
        
        # Merge with off-chain data
        merged = pd.merge(
            onchain_df,
            self.offchain_data,
            on='day',
            how='left'
        )
        
        # Fill missing off-chain data with 0
        for col in OFFCHAIN_FEATURES:
            if col in merged.columns:
                merged[col] = merged[col].fillna(0)
            else:
                merged[col] = 0
        
        return merged
    
    def validate_csv_columns(self, df: pd.DataFrame) -> tuple[bool, List[str]]:
        """Validate that CSV has required columns"""
        required = ['address', 'day'] + ONCHAIN_FEATURES
        missing = [col for col in required if col not in df.columns]
        return len(missing) == 0, missing
    
    def extract_features(self, row: pd.Series) -> Dict:
        """Extract on-chain and off-chain features from a row"""
        on_chain = {col: float(row.get(col, 0)) for col in ONCHAIN_FEATURES}
        off_chain = {col: float(row.get(col, 0)) for col in OFFCHAIN_FEATURES}
        return {'on_chain': on_chain, 'off_chain': off_chain}


# Singleton instance
data_service = DataService()
