"""
Data loading and caching utilities for the dashboard
"""
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional
import yaml


class DataLoader:
    """Centralized data loader with caching"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize data loader"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.data_dir = Path("data/generated")
        self.report_date = pd.to_datetime(self.config['data']['report_date'])

    @st.cache_data(ttl=3600)
    def load_passenger_data(_self) -> Dict[str, pd.DataFrame]:
        """Load all passenger-related datasets"""
        return {
            'daily': pd.read_parquet(_self.data_dir / 'pax_daily_volumes.parquet'),
            'hourly_showup': pd.read_parquet(_self.data_dir / 'pax_hourly_showup.parquet'),
            'by_airline': pd.read_parquet(_self.data_dir / 'pax_by_airline.parquet')
        }

    @st.cache_data(ttl=3600)
    def load_atm_data(_self) -> pd.DataFrame:
        """Load ATM data"""
        return pd.read_parquet(_self.data_dir / 'atm_daily.parquet')

    @st.cache_data(ttl=3600)
    def load_queue_data(_self) -> Dict[str, pd.DataFrame]:
        """Load queue time and compliance data"""
        return {
            'zone_compliance': pd.read_parquet(_self.data_dir / 'queue_zone_compliance.parquet'),
            'hourly_compliance': pd.read_parquet(_self.data_dir / 'queue_hourly_compliance.parquet')
        }

    @st.cache_data(ttl=3600)
    def load_security_data(_self) -> Dict[str, pd.DataFrame]:
        """Load security lane data"""
        return {
            'daily': pd.read_parquet(_self.data_dir / 'security_lanes_daily.parquet'),
            'hourly': pd.read_parquet(_self.data_dir / 'security_lanes_hourly.parquet')
        }

    @st.cache_data(ttl=3600)
    def load_baggage_data(_self) -> pd.DataFrame:
        """Load baggage utilization data"""
        return pd.read_parquet(_self.data_dir / 'baggage_utilization.parquet')

    @st.cache_data(ttl=3600)
    def load_gate_data(_self) -> pd.DataFrame:
        """Load gate utilization data"""
        return pd.read_parquet(_self.data_dir / 'gate_utilization.parquet')

    @st.cache_data(ttl=3600)
    def load_biometric_data(_self) -> pd.DataFrame:
        """Load biometric adoption data"""
        return pd.read_parquet(_self.data_dir / 'biometric_adoption.parquet')

    @st.cache_data(ttl=3600)
    def load_voc_data(_self) -> Dict[str, pd.DataFrame]:
        """Load Voice of Customer data"""
        return {
            'feedback': pd.read_parquet(_self.data_dir / 'voc_feedback.parquet'),
            'messages': pd.read_parquet(_self.data_dir / 'voc_messages.parquet')
        }

    def load_all_data(self) -> Dict[str, any]:
        """Load all datasets at once"""
        return {
            'passenger': self.load_passenger_data(),
            'atm': self.load_atm_data(),
            'queue': self.load_queue_data(),
            'security': self.load_security_data(),
            'baggage': self.load_baggage_data(),
            'gate': self.load_gate_data(),
            'biometric': self.load_biometric_data(),
            'voc': self.load_voc_data()
        }

    def filter_by_date(self, df: pd.DataFrame, date_col: str, start_date=None, end_date=None) -> pd.DataFrame:
        """Filter DataFrame by date range"""
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])

        if start_date:
            df = df[df[date_col] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df[date_col] <= pd.to_datetime(end_date)]

        return df

    def get_report_date_data(self, df: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
        """Get data for the configured report date"""
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        return df[df[date_col] == self.report_date]
