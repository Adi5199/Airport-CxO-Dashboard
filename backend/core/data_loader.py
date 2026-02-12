import pandas as pd
from pathlib import Path
from typing import Dict
from backend.core.config import CONFIG, DATA_DIR


class DataLoader:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.report_date = pd.to_datetime(CONFIG["data"]["report_date"])
        self._passenger_data = None
        self._atm_data = None
        self._queue_data = None
        self._security_data = None
        self._baggage_data = None
        self._gate_data = None
        self._biometric_data = None
        self._voc_data = None

    def load_all(self):
        self.load_passenger_data()
        self.load_atm_data()
        self.load_queue_data()
        self.load_security_data()
        self.load_baggage_data()
        self.load_gate_data()
        self.load_biometric_data()
        self.load_voc_data()

    def load_passenger_data(self) -> Dict[str, pd.DataFrame]:
        if self._passenger_data is None:
            self._passenger_data = {
                "daily": pd.read_parquet(self.data_dir / "pax_daily_volumes.parquet"),
                "hourly_showup": pd.read_parquet(self.data_dir / "pax_hourly_showup.parquet"),
                "by_airline": pd.read_parquet(self.data_dir / "pax_by_airline.parquet"),
            }
        return self._passenger_data

    def load_atm_data(self) -> pd.DataFrame:
        if self._atm_data is None:
            self._atm_data = pd.read_parquet(self.data_dir / "atm_daily.parquet")
        return self._atm_data

    def load_queue_data(self) -> Dict[str, pd.DataFrame]:
        if self._queue_data is None:
            self._queue_data = {
                "zone_compliance": pd.read_parquet(self.data_dir / "queue_zone_compliance.parquet"),
                "hourly_compliance": pd.read_parquet(self.data_dir / "queue_hourly_compliance.parquet"),
            }
        return self._queue_data

    def load_security_data(self) -> Dict[str, pd.DataFrame]:
        if self._security_data is None:
            self._security_data = {
                "daily": pd.read_parquet(self.data_dir / "security_lanes_daily.parquet"),
                "hourly": pd.read_parquet(self.data_dir / "security_lanes_hourly.parquet"),
            }
        return self._security_data

    def load_baggage_data(self) -> pd.DataFrame:
        if self._baggage_data is None:
            self._baggage_data = pd.read_parquet(self.data_dir / "baggage_utilization.parquet")
        return self._baggage_data

    def load_gate_data(self) -> pd.DataFrame:
        if self._gate_data is None:
            self._gate_data = pd.read_parquet(self.data_dir / "gate_utilization.parquet")
        return self._gate_data

    def load_biometric_data(self) -> pd.DataFrame:
        if self._biometric_data is None:
            self._biometric_data = pd.read_parquet(self.data_dir / "biometric_adoption.parquet")
        return self._biometric_data

    def load_voc_data(self) -> Dict[str, pd.DataFrame]:
        if self._voc_data is None:
            self._voc_data = {
                "feedback": pd.read_parquet(self.data_dir / "voc_feedback.parquet"),
                "messages": pd.read_parquet(self.data_dir / "voc_messages.parquet"),
            }
        return self._voc_data
