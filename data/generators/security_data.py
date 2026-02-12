"""
Security lanes performance data generator
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from base_generator import BaseDataGenerator


class SecurityDataGenerator(BaseDataGenerator):
    """Generate security lane performance data"""

    def __init__(self):
        super().__init__()
        self.t1_lanes = self.config['operations']['terminals']['T1']['security_lanes']
        self.t2_lanes = self.config['operations']['terminals']['T2']['security_lanes']

    def generate_lane_performance(self) -> pd.DataFrame:
        """
        Generate security lane cleared volumes and reject rates
        """
        dates = self.generate_date_range()
        records = []

        all_lanes = self.t1_lanes + self.t2_lanes

        for date in dates:
            dow = date.dayofweek
            is_weekend = dow >= 5
            weekend_mult = 1.2 if is_weekend else 1.0

            for lane in all_lanes:
                # Determine terminal
                terminal = 'T1' if lane.startswith('T1') else 'T2'

                # Determine lane group
                if 'Left' in lane:
                    lane_group = 'Left'
                elif 'Right' in lane:
                    lane_group = 'Right'
                elif 'Intl' in lane:
                    lane_group = 'International'
                else:
                    lane_group = 'Swing'

                # Base cleared volume per lane per day
                if 'Intl' in lane:
                    base_cleared = int(np.random.normal(1200, 200) * weekend_mult)
                else:
                    base_cleared = int(np.random.normal(1800, 250) * weekend_mult)

                # Reject rate (normally 2-5%, some lanes worse)
                base_reject_rate = np.random.uniform(2.0, 5.0)

                # Some lanes have higher reject rates (for demo)
                if lane in ['T1-Left-L3', 'T2-Left-L6']:
                    base_reject_rate = np.random.uniform(6.5, 9.5)

                reject_count = int(base_cleared * (base_reject_rate / 100))
                total_scanned = base_cleared + reject_count

                records.append({
                    'date': date,
                    'lane': lane,
                    'terminal': terminal,
                    'lane_group': lane_group,
                    'cleared_volume': base_cleared,
                    'reject_count': reject_count,
                    'total_scanned': total_scanned,
                    'reject_rate_pct': round(base_reject_rate, 2),
                    'avg_throughput_per_hour': round(base_cleared / 16, 1)  # 16 hour operation
                })

        df = pd.DataFrame(records)

        # Inject anomaly on report_date - certain lanes have higher rejects
        anomaly_lanes = ['T2-Left-L6', 'T1-Left-L3']
        for lane in anomaly_lanes:
            mask = (df['date'] == self.report_date) & (df['lane'] == lane)
            df.loc[mask, 'reject_rate_pct'] = np.random.uniform(11.5, 14.5)
            df.loc[mask, 'reject_count'] = (
                df.loc[mask, 'cleared_volume'] * df.loc[mask, 'reject_rate_pct'] / 100
            ).astype(int)

        return df

    def generate_hourly_lane_performance(self) -> pd.DataFrame:
        """
        Generate hourly lane performance for detailed analysis
        """
        dates = self.generate_date_range()
        records = []

        # Focus on key lanes for hourly detail
        key_lanes = ['T1-Left-L1', 'T1-Left-L3', 'T2-Left-L4', 'T2-Left-L6', 'T2-Right-R4']

        for date in dates:
            for lane in key_lanes:
                terminal = 'T1' if lane.startswith('T1') else 'T2'

                for hour in range(5, 23):  # 5 AM to 10 PM
                    # Peak hours have higher volume
                    if hour in [7, 8, 14, 15, 18, 19]:
                        base_cleared = int(np.random.normal(140, 25))
                    else:
                        base_cleared = int(np.random.normal(80, 20))

                    # Reject rate
                    if lane in ['T1-Left-L3', 'T2-Left-L6']:
                        reject_rate = np.random.uniform(6.0, 10.0)
                    else:
                        reject_rate = np.random.uniform(2.0, 5.0)

                    reject_count = int(base_cleared * (reject_rate / 100))

                    records.append({
                        'date': date,
                        'hour': hour,
                        'lane': lane,
                        'terminal': terminal,
                        'cleared_volume': base_cleared,
                        'reject_count': reject_count,
                        'reject_rate_pct': round(reject_rate, 2)
                    })

        df = pd.DataFrame(records)

        # Inject anomaly at report_date 14:00-16:00
        for hour in [14, 15, 16]:
            mask = (
                (df['date'] == self.report_date) &
                (df['lane'].isin(['T2-Left-L6', 'T1-Left-L3'])) &
                (df['hour'] == hour)
            )
            df.loc[mask, 'reject_rate_pct'] = np.random.uniform(12.5, 16.0)
            df.loc[mask, 'reject_count'] = (
                df.loc[mask, 'cleared_volume'] * df.loc[mask, 'reject_rate_pct'] / 100
            ).astype(int)

        return df

    def generate_all(self):
        """Generate all security lane datasets"""
        print("Generating Security Lane Data...")

        # Daily lane performance
        daily_lanes = self.generate_lane_performance()
        self.save_to_parquet(daily_lanes, 'security_lanes_daily.parquet')

        # Hourly lane performance
        hourly_lanes = self.generate_hourly_lane_performance()
        self.save_to_parquet(hourly_lanes, 'security_lanes_hourly.parquet')

        print("✓ Security lane data generation complete\n")


if __name__ == "__main__":
    generator = SecurityDataGenerator()
    generator.generate_all()
