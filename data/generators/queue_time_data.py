"""
Queue time and compliance data generator
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from base_generator import BaseDataGenerator


class QueueTimeDataGenerator(BaseDataGenerator):
    """Generate queue time and compliance metrics"""

    def __init__(self):
        super().__init__()
        self.targets = self.config['targets']['queue_time']

    def generate_zone_compliance(self) -> pd.DataFrame:
        """
        Generate KPI compliance data for all zones
        (Departure Entry, Check-in, Security)
        """
        dates = self.generate_date_range()
        records = []

        # Define zones with their thresholds
        zones = [
            {'zone': 'Departure Entry 1-4', 'terminal': 'T1', 'threshold_min': 5, 'type': 'Entry'},
            {'zone': 'Departure Entry 5a-9', 'terminal': 'T2', 'threshold_min': 5, 'type': 'Entry'},
            {'zone': 'Check-in 1-33', 'terminal': 'T1', 'threshold_min': 10, 'type': 'Checkin'},
            {'zone': 'Check-in 34-86', 'terminal': 'T2', 'threshold_min': 10, 'type': 'Checkin'},
            {'zone': 'Domestic Security Left', 'terminal': 'T1', 'threshold_min': 15, 'type': 'Security'},
            {'zone': 'Domestic Security Right', 'terminal': 'T1', 'threshold_min': 15, 'type': 'Security'},
            {'zone': 'T2 Security Left', 'terminal': 'T2', 'threshold_min': 20, 'type': 'Security'},
            {'zone': 'T2 Security Right', 'terminal': 'T2', 'threshold_min': 20, 'type': 'Security'},
        ]

        # Time windows for the day
        time_windows = [
            '0500-0700', '0700-0900', '0900-1100', '1100-1300',
            '1300-1500', '1500-1700', '1700-1900', '1900-2100', '2100-2300'
        ]

        for date in dates:
            for zone_info in zones:
                for window in time_windows:
                    # Base compliance (usually high ~92-98%)
                    base_compliance = np.random.normal(95, 2.5)

                    # Peak hours have lower compliance
                    if window in ['0700-0900', '1400-1600', '1800-2000']:
                        base_compliance -= np.random.uniform(3, 8)

                    # Weekend boost
                    if date.dayofweek >= 5:
                        base_compliance += 2

                    # Clip to realistic range
                    compliance_pct = np.clip(base_compliance, 75, 99.5)

                    # Calculate passengers processed
                    pax_in_window = int(np.random.normal(800, 150))

                    # Passengers meeting threshold
                    pax_meeting_threshold = int(pax_in_window * (compliance_pct / 100))

                    # Average wait time
                    avg_wait = zone_info['threshold_min'] * np.random.uniform(0.4, 0.9)

                    records.append({
                        'date': date,
                        'zone': zone_info['zone'],
                        'terminal': zone_info['terminal'],
                        'zone_type': zone_info['type'],
                        'time_window': window,
                        'threshold_minutes': zone_info['threshold_min'],
                        'target_compliance_pct': 95.0,
                        'actual_compliance_pct': round(compliance_pct, 2),
                        'pax_total': pax_in_window,
                        'pax_meeting_threshold': pax_meeting_threshold,
                        'avg_wait_time_min': round(avg_wait, 2),
                        'variance_from_target': round(compliance_pct - 95.0, 2)
                    })

        df = pd.DataFrame(records)

        # INJECT DEMO ANOMALY for use case
        # On report_date, 1400-1600, Check-in 34-86 and T2 Security have poor performance
        report_date = self.report_date
        anomaly_zones = ['Check-in 34-86', 'T2 Security Left', 'T2 Security Right']
        anomaly_windows = ['1400-1600', '1500-1700', '1600-1800']

        for zone in anomaly_zones:
            for window in anomaly_windows:
                mask = (
                    (df['date'] == report_date) &
                    (df['zone'] == zone) &
                    (df['time_window'] == window)
                )
                # Drop compliance significantly
                df.loc[mask, 'actual_compliance_pct'] = np.random.uniform(78, 85)
                df.loc[mask, 'variance_from_target'] = df.loc[mask, 'actual_compliance_pct'] - 95.0
                df.loc[mask, 'avg_wait_time_min'] *= 1.6

        return df

    def generate_hourly_compliance(self) -> pd.DataFrame:
        """
        Generate hourly compliance data (for detailed drill-down)
        """
        dates = self.generate_date_range()
        records = []

        zones = [
            {'zone': 'Departure Entry 1-4', 'terminal': 'T1', 'threshold_min': 5},
            {'zone': 'Departure Entry 5a-9', 'terminal': 'T2', 'threshold_min': 5},
            {'zone': 'Check-in 1-33', 'terminal': 'T1', 'threshold_min': 10},
            {'zone': 'Check-in 34-86', 'terminal': 'T2', 'threshold_min': 10},
            {'zone': 'Domestic Security Left', 'terminal': 'T1', 'threshold_min': 15},
            {'zone': 'Domestic Security Right', 'terminal': 'T1', 'threshold_min': 15},
        ]

        for date in dates:
            for zone_info in zones:
                for hour in range(5, 24):  # 5 AM to 11 PM
                    # Base compliance
                    base_compliance = np.random.normal(95, 3)

                    # Peak hours
                    if hour in [7, 8, 14, 15, 18, 19]:
                        base_compliance -= np.random.uniform(4, 10)

                    compliance_pct = np.clip(base_compliance, 70, 99.8)

                    pax = int(np.random.normal(350, 80))
                    pax_meeting = int(pax * (compliance_pct / 100))

                    records.append({
                        'date': date,
                        'hour': hour,
                        'zone': zone_info['zone'],
                        'terminal': zone_info['terminal'],
                        'threshold_minutes': zone_info['threshold_min'],
                        'actual_compliance_pct': round(compliance_pct, 2),
                        'target_compliance_pct': 95.0,
                        'pax_total': pax,
                        'pax_meeting_threshold': pax_meeting
                    })

        df = pd.DataFrame(records)

        # Inject anomaly at report_date 14:00-16:00 for Check-in 34-86
        for hour in [14, 15, 16]:
            mask = (
                (df['date'] == self.report_date) &
                (df['zone'] == 'Check-in 34-86') &
                (df['hour'] == hour)
            )
            df.loc[mask, 'actual_compliance_pct'] = np.random.uniform(76, 82)

        return df

    def generate_all(self):
        """Generate all queue time datasets"""
        print("Generating Queue Time & Compliance Data...")

        # Zone compliance by time window
        zone_compliance = self.generate_zone_compliance()
        self.save_to_parquet(zone_compliance, 'queue_zone_compliance.parquet')

        # Hourly compliance
        hourly_compliance = self.generate_hourly_compliance()
        self.save_to_parquet(hourly_compliance, 'queue_hourly_compliance.parquet')

        print("✓ Queue time data generation complete\n")


if __name__ == "__main__":
    generator = QueueTimeDataGenerator()
    generator.generate_all()
