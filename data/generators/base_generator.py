"""
Base data generator with common utilities for all data generators
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import yaml


class BaseDataGenerator:
    """Base class for all data generators"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize with configuration"""
        # Handle relative paths from different locations
        import os
        if not os.path.exists(config_path):
            # Try from project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(project_root, 'config.yaml')

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.start_date = pd.to_datetime(self.config['data']['start_date'])
        self.end_date = pd.to_datetime(self.config['data']['end_date'])
        self.report_date = pd.to_datetime(self.config['data']['report_date'])

        # Set random seed for reproducibility
        np.random.seed(42)

    def generate_date_range(self, freq: str = 'D') -> pd.DatetimeIndex:
        """Generate date range for the configured period"""
        return pd.date_range(self.start_date, self.end_date, freq=freq)

    def generate_hourly_profile(self,
                                date: datetime,
                                base_volume: int,
                                peak_hours: List[Tuple[int, float]] = None) -> pd.DataFrame:
        """
        Generate realistic hourly passenger profile with peaks

        Args:
            date: Date for the profile
            base_volume: Base number of passengers/movements for the day
            peak_hours: List of (hour, multiplier) tuples for peak periods
                       Default creates typical airport peaks

        Returns:
            DataFrame with hourly distribution
        """
        if peak_hours is None:
            # Default airport traffic pattern
            # Morning peak (6-9 AM), Afternoon (2-4 PM), Evening (6-8 PM)
            peak_hours = [
                (6, 1.5), (7, 2.0), (8, 1.8), (9, 1.3),
                (14, 1.4), (15, 1.5), (16, 1.3),
                (18, 1.6), (19, 1.7), (20, 1.4)
            ]

        # Create hourly weights
        hourly_weights = np.ones(24) * 0.3  # Low baseline
        for hour, multiplier in peak_hours:
            hourly_weights[hour] = multiplier

        # Add some randomness
        hourly_weights = hourly_weights * np.random.uniform(0.9, 1.1, 24)

        # Normalize to sum to base_volume
        hourly_volumes = (hourly_weights / hourly_weights.sum() * base_volume).astype(int)

        # Create DataFrame
        hours = pd.date_range(
            start=date.replace(hour=0, minute=0, second=0),
            periods=24,
            freq='H'
        )

        df = pd.DataFrame({
            'datetime': hours,
            'hour': hours.hour,
            'volume': hourly_volumes
        })

        return df

    def add_anomaly(self,
                    df: pd.DataFrame,
                    date: datetime,
                    hour: int,
                    column: str,
                    anomaly_type: str = 'spike',
                    magnitude: float = 0.5) -> pd.DataFrame:
        """
        Inject anomalies into data for demo purposes

        Args:
            df: DataFrame to modify
            date: Date of anomaly
            hour: Hour of anomaly
            column: Column to modify
            anomaly_type: 'spike' or 'drop'
            magnitude: Magnitude of change (0-1 for percentage)
        """
        mask = (df['datetime'].dt.date == date.date()) & (df['hour'] == hour)

        if anomaly_type == 'spike':
            df.loc[mask, column] = df.loc[mask, column] * (1 + magnitude)
        elif anomaly_type == 'drop':
            df.loc[mask, column] = df.loc[mask, column] * (1 - magnitude)

        return df

    def calculate_7day_average(self, df: pd.DataFrame, value_col: str, date_col: str = 'date') -> pd.DataFrame:
        """Calculate trailing 7-day average"""
        df = df.sort_values(date_col)
        df[f'{value_col}_7day_avg'] = df[value_col].rolling(window=7, min_periods=1).mean()
        df[f'{value_col}_vs_7day_pct'] = ((df[value_col] - df[f'{value_col}_7day_avg']) /
                                           df[f'{value_col}_7day_avg'] * 100).round(2)
        return df

    def save_to_csv(self, df: pd.DataFrame, filename: str):
        """Save DataFrame to CSV in the generated folder"""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_path = os.path.join(project_root, "data", "generated", filename)
        df.to_csv(output_path, index=False)
        print(f"✓ Generated: {filename} ({len(df):,} rows)")
        return output_path

    def save_to_parquet(self, df: pd.DataFrame, filename: str):
        """Save DataFrame to Parquet in the generated folder"""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_path = os.path.join(project_root, "data", "generated", filename)
        df.to_parquet(output_path, index=False)
        print(f"✓ Generated: {filename} ({len(df):,} rows)")
        return output_path
