import pandas as pd
import numpy as np
from typing import List, Tuple


class MetricsCalculator:
    @staticmethod
    def calculate_compliance_score(actual_pct: float, target_pct: float) -> str:
        if actual_pct >= target_pct:
            return "On Target"
        elif actual_pct >= target_pct - 3:
            return "Near Target"
        else:
            return "Below Target"

    @staticmethod
    def calculate_trend(current_value: float, previous_value: float) -> Tuple[str, float, str]:
        if previous_value == 0:
            return ("flat", 0.0, "gray")
        pct_change = ((current_value - previous_value) / previous_value) * 100
        if abs(pct_change) < 1:
            return ("flat", pct_change, "gray")
        elif pct_change > 0:
            return ("up", pct_change, "green")
        else:
            return ("down", pct_change, "red")

    @staticmethod
    def find_peak_hours(df: pd.DataFrame, value_col: str, hour_col: str = "hour", top_n: int = 3) -> List[int]:
        hourly_sum = df.groupby(hour_col)[value_col].sum().nlargest(top_n)
        return hourly_sum.index.tolist()


class AnomalyDetector:
    @staticmethod
    def detect_queue_anomalies(df: pd.DataFrame, target_pct: float = 95.0) -> pd.DataFrame:
        df = df.copy()
        df["is_anomaly"] = df["actual_compliance_pct"] < target_pct

        def classify_severity(variance):
            if variance >= -3:
                return "Low"
            elif variance >= -7:
                return "Medium"
            else:
                return "High"

        df["anomaly_severity"] = df["variance_from_target"].apply(classify_severity)
        return df[df["is_anomaly"]]

    @staticmethod
    def detect_security_lane_anomalies(df: pd.DataFrame, reject_threshold: float = 8.0) -> pd.DataFrame:
        df = df.copy()
        df["high_reject"] = df["reject_rate_pct"] > reject_threshold
        throughput_threshold = df["cleared_volume"].quantile(0.25)
        df["low_throughput"] = df["cleared_volume"] < throughput_threshold
        df["is_anomaly"] = df["high_reject"] | df["low_throughput"]
        return df[df["is_anomaly"]]
