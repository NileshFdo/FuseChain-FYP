import pandas as pd
from typing import List, Optional, Dict
from pathlib import Path

from app.config import get_train_data_path, get_offchain_data_path, ONCHAIN_FEATURES, OFFCHAIN_FEATURES


class DataService:
    
    def __init__(self):
        self._train_data = None
        self._offchain_data = None
        self._address_cache = None
    
    def load_data(self):
        train_path = get_train_data_path()
        print(f"Loading training data from {train_path}...")
        self._train_data = pd.read_parquet(train_path)
        self._train_data['day'] = pd.to_datetime(self._train_data['day']).dt.strftime('%Y-%m-%d')
        print(f"Loaded {len(self._train_data):,} rows")
        
        offchain_path = get_offchain_data_path()
        print(f"Loading off-chain data from {offchain_path}...")
        self._offchain_data = pd.read_parquet(offchain_path)
        self._offchain_data['day'] = pd.to_datetime(self._offchain_data['day']).dt.strftime('%Y-%m-%d')
        print(f"Loaded {len(self._offchain_data):,} rows")
        
        self._address_cache = self._train_data['address'].unique().tolist()
        print(f"Cached {len(self._address_cache):,} unique addresses")
    
    @property
    def train_data(self):
        if self._train_data is None:
            self.load_data()
        return self._train_data
    
    @property
    def offchain_data(self):
        if self._offchain_data is None:
            self.load_data()
        return self._offchain_data
    
    def get_addresses(self, search=None, limit=100):
        if self._address_cache is None:
            self.load_data()
        
        addresses = self._address_cache
        if search:
            search_lower = search.lower()
            addresses = [a for a in addresses if search_lower in a.lower()]
        
        return addresses[:limit]
    
    def get_address_data(self, address):
        mask = self.train_data['address'].str.lower() == address.lower()
        data = self.train_data[mask].copy()
        
        if len(data) == 0:
            return None
        return data.sort_values('day')
    
    def address_exists(self, address):
        if self._address_cache is None:
            self.load_data()
        return address.lower() in [a.lower() for a in self._address_cache]
    
    def merge_with_offchain(self, onchain_df):
        # make sure dates match
        onchain_df = onchain_df.copy()
        onchain_df['day'] = pd.to_datetime(onchain_df['day']).dt.strftime('%Y-%m-%d')
        
        merged = pd.merge(onchain_df, self.offchain_data, on='day', how='left')
        
        # fill missing offchain with 0
        for col in OFFCHAIN_FEATURES:
            if col in merged.columns:
                merged[col] = merged[col].fillna(0)
            else:
                merged[col] = 0
        
        return merged
    
    def validate_csv_columns(self, df):
        required = ['address', 'day'] + ONCHAIN_FEATURES
        missing = [col for col in required if col not in df.columns]
        return len(missing) == 0, missing
    
    def extract_features(self, row):
        on_chain = {col: float(row.get(col, 0)) for col in ONCHAIN_FEATURES}
        off_chain = {col: float(row.get(col, 0)) for col in OFFCHAIN_FEATURES}
        return {'on_chain': on_chain, 'off_chain': off_chain}


data_service = DataService()
