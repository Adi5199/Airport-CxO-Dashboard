"""
Calculation and transformation utilities for dashboard metrics
"""
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict


class MetricsCalculator:
    """Calculate various metrics and KPIs"""

    @staticmethod
    def calculate_compliance_score(actual_pct: float, target_pct: float) -> str:
        """Determine compliance status"""
        if actual_pct >= target_pct:
            return "✓ On Target"
        elif actual_pct >= target_pct - 3:
            return "⚠ Near Target"
        else:
            return "✗ Below Target"

    @staticmethod
    def calculate_trend(current_value: float, previous_value: float) -> Tuple[str, float, str]:
        """
        Calculate trend indicator
        Returns: (icon, percentage_change, color)
        """
        if previous_value == 0:
            return ("→", 0.0, "gray")

        pct_change = ((current_value - previous_value) / previous_value) * 100

        if abs(pct_change) < 1:
            return ("→", pct_change, "gray")
        elif pct_change > 0:
            return ("↑", pct_change, "green")
        else:
            return ("↓", pct_change, "red")

    @staticmethod
    def find_peak_hours(df: pd.DataFrame, value_col: str, hour_col: str = 'hour', top_n: int = 3) -> List[int]:
        """Find top N peak hours by volume"""
        hourly_sum = df.groupby(hour_col)[value_col].sum().nlargest(top_n)
        return hourly_sum.index.tolist()

    @staticmethod
    def detect_anomalies(df: pd.DataFrame, value_col: str, threshold_std: float = 2.0) -> pd.DataFrame:
        """
        Detect anomalies using standard deviation method
        Marks values beyond threshold_std standard deviations as anomalies
        """
        df = df.copy()
        mean = df[value_col].mean()
        std = df[value_col].std()

        df['is_anomaly'] = np.abs(df[value_col] - mean) > (threshold_std * std)
        df['z_score'] = (df[value_col] - mean) / std

        return df

    @staticmethod
    def calculate_boarding_mode_mix(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate boarding mode distribution"""
        mode_counts = df.groupby(['date', 'terminal', 'boarding_mode']).agg({
            'flights': 'sum',
            'pax': 'sum'
        }).reset_index()

        # Calculate percentages
        totals = mode_counts.groupby(['date', 'terminal'])[['flights', 'pax']].transform('sum')
        mode_counts['flights_pct'] = (mode_counts['flights'] / totals['flights'] * 100).round(2)
        mode_counts['pax_pct'] = (mode_counts['pax'] / totals['pax'] * 100).round(2)

        return mode_counts

    @staticmethod
    def rank_by_metric(df: pd.DataFrame, group_col: str, value_col: str, ascending: bool = False) -> pd.DataFrame:
        """Rank items by a metric"""
        df = df.copy()
        df['rank'] = df[value_col].rank(ascending=ascending, method='dense').astype(int)
        return df.sort_values('rank')

    @staticmethod
    def calculate_utilization_score(actual: float, capacity: float) -> Tuple[float, str]:
        """
        Calculate utilization percentage and status
        Returns: (utilization_pct, status)
        """
        util_pct = (actual / capacity * 100) if capacity > 0 else 0

        if util_pct < 60:
            status = "Under-utilized"
        elif util_pct <= 85:
            status = "Optimal"
        elif util_pct <= 95:
            status = "Near Capacity"
        else:
            status = "Over-utilized"

        return round(util_pct, 1), status

    @staticmethod
    def aggregate_by_time_bucket(df: pd.DataFrame, date_col: str, value_cols: List[str],
                                  bucket: str = 'L7D') -> pd.DataFrame:
        """
        Aggregate data by time bucket (L7D, L30D, MTD, YTD)
        """
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])

        max_date = df[date_col].max()

        if bucket == 'L7D':
            start_date = max_date - pd.Timedelta(days=7)
        elif bucket == 'L30D':
            start_date = max_date - pd.Timedelta(days=30)
        elif bucket == 'MTD':
            start_date = max_date.replace(day=1)
        elif bucket == 'YTD':
            start_date = max_date.replace(month=1, day=1)
        else:
            raise ValueError(f"Unknown time bucket: {bucket}")

        filtered = df[df[date_col] >= start_date]

        # Aggregate
        agg_dict = {col: 'sum' for col in value_cols}
        result = filtered.agg(agg_dict)

        return result

    @staticmethod
    def calculate_voc_ratio(compliments: int, complaints: int) -> Tuple[float, str]:
        """
        Calculate compliments to complaints ratio and sentiment
        Returns: (ratio, sentiment_label)
        """
        if complaints == 0:
            return (float('inf'), "Excellent")

        ratio = compliments / complaints

        if ratio >= 3.0:
            sentiment = "Excellent"
        elif ratio >= 2.0:
            sentiment = "Good"
        elif ratio >= 1.0:
            sentiment = "Fair"
        else:
            sentiment = "Needs Attention"

        return round(ratio, 2), sentiment


class AnomalyDetector:
    """Detect and flag anomalies for executive attention"""

    @staticmethod
    def detect_queue_anomalies(df: pd.DataFrame, target_pct: float = 95.0) -> pd.DataFrame:
        """Detect queue compliance anomalies"""
        df = df.copy()

        # Flag compliance below target
        df['is_anomaly'] = df['actual_compliance_pct'] < target_pct

        # Severity
        def classify_severity(variance):
            if variance >= -3:
                return "Low"
            elif variance >= -7:
                return "Medium"
            else:
                return "High"

        df['anomaly_severity'] = df['variance_from_target'].apply(classify_severity)

        return df[df['is_anomaly']]

    @staticmethod
    def detect_security_lane_anomalies(df: pd.DataFrame, reject_threshold: float = 8.0) -> pd.DataFrame:
        """Detect security lane anomalies"""
        df = df.copy()

        # High reject rate
        df['high_reject'] = df['reject_rate_pct'] > reject_threshold

        # Low throughput (bottom 25%)
        throughput_threshold = df['cleared_volume'].quantile(0.25)
        df['low_throughput'] = df['cleared_volume'] < throughput_threshold

        # Combined anomaly flag
        df['is_anomaly'] = df['high_reject'] | df['low_throughput']

        return df[df['is_anomaly']]

    @staticmethod
    def detect_voc_anomalies(df: pd.DataFrame, ratio_threshold: float = 1.5) -> pd.DataFrame:
        """Detect negative VOC trends"""
        df = df.copy()

        # Calculate ratio
        df['ratio'] = df['compliments'] / df['complaints'].replace(0, 1)

        # Flag low ratios
        df['is_anomaly'] = df['ratio'] < ratio_threshold

        return df[df['is_anomaly']]
