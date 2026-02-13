"""
Operational KPI data generator - OTP, Baggage Delivery, Slot Adherence, Safety Issues
"""
import pandas as pd
import numpy as np
from base_generator import BaseDataGenerator


class OperationalKPIDataGenerator(BaseDataGenerator):
    """Generate OTP, Baggage Delivery, Slot Adherence, Safety data"""

    def generate_otp_data(self) -> pd.DataFrame:
        """Generate On-Time Performance data"""
        dates = self.generate_date_range()
        records = []

        for date in dates:
            dow = date.dayofweek
            # Slightly worse OTP on weekends due to congestion
            base_otp = 87 if dow >= 5 else 90

            for terminal in ["T1", "T2"]:
                for pax_type in ["Domestic", "International"]:
                    if terminal == "T1" and pax_type == "International":
                        continue  # T1 is domestic only

                    otp = np.clip(np.random.normal(base_otp, 4), 60, 99)
                    total_flights = int(np.random.normal(55 if terminal == "T1" else 40, 5))
                    on_time = int(total_flights * otp / 100)
                    delayed = total_flights - on_time
                    avg_delay_min = round(np.random.normal(12, 4), 1) if delayed > 0 else 0

                    records.append({
                        "date": date,
                        "terminal": terminal,
                        "passenger_type": pax_type,
                        "total_flights": total_flights,
                        "on_time_flights": on_time,
                        "delayed_flights": delayed,
                        "otp_pct": round(otp, 1),
                        "avg_delay_minutes": max(0, avg_delay_min),
                    })

        return pd.DataFrame(records)

    def generate_baggage_delivery_data(self) -> pd.DataFrame:
        """Generate baggage delivery performance data"""
        dates = self.generate_date_range()
        records = []

        for date in dates:
            for terminal in ["T1", "T2"]:
                total_bags = int(np.random.normal(8000 if terminal == "T1" else 6500, 500))
                delivered_in_target = int(total_bags * np.clip(np.random.normal(0.92, 0.03), 0.8, 0.99))
                first_bag_min = round(np.random.normal(14, 3), 1)
                last_bag_min = round(np.random.normal(28, 5), 1)
                mishandled = int(np.random.exponential(3))

                records.append({
                    "date": date,
                    "terminal": terminal,
                    "total_bags": total_bags,
                    "delivered_within_target": delivered_in_target,
                    "delivery_pct": round(delivered_in_target / total_bags * 100, 1),
                    "first_bag_minutes": max(5, first_bag_min),
                    "last_bag_minutes": max(15, last_bag_min),
                    "mishandled_bags": mishandled,
                })

        return pd.DataFrame(records)

    def generate_slot_adherence_data(self) -> pd.DataFrame:
        """Generate slot adherence data"""
        dates = self.generate_date_range()
        records = []

        for date in dates:
            for terminal in ["T1", "T2"]:
                total_slots = int(np.random.normal(110 if terminal == "T1" else 90, 8))
                adherence_pct = np.clip(np.random.normal(88, 5), 70, 99)
                adhered = int(total_slots * adherence_pct / 100)
                early = int((total_slots - adhered) * 0.3)
                late = total_slots - adhered - early

                records.append({
                    "date": date,
                    "terminal": terminal,
                    "total_slots": total_slots,
                    "adhered_slots": adhered,
                    "early_slots": early,
                    "late_slots": late,
                    "adherence_pct": round(adherence_pct, 1),
                })

        return pd.DataFrame(records)

    def generate_safety_data(self) -> pd.DataFrame:
        """Generate safety issues data"""
        dates = self.generate_date_range()
        records = []
        categories = ["Runway Incursion", "FOD Detection", "Bird Strike", "Equipment Malfunction", "Weather Related", "Ground Incident"]

        for date in dates:
            for terminal in ["T1", "T2"]:
                # Most days have 0-3 safety issues
                n_issues = np.random.poisson(1.2)
                if n_issues > 0:
                    chosen_cats = np.random.choice(categories, size=min(n_issues, len(categories)), replace=False)
                    for cat in chosen_cats:
                        severity = np.random.choice(["Low", "Medium", "High"], p=[0.6, 0.3, 0.1])
                        records.append({
                            "date": date,
                            "terminal": terminal,
                            "category": cat,
                            "severity": severity,
                            "resolved": np.random.choice([True, False], p=[0.85, 0.15]),
                        })

        return pd.DataFrame(records)

    def generate_all(self):
        print("Generating Operational KPI Data...")
        otp = self.generate_otp_data()
        self.save_to_parquet(otp, "otp_daily.parquet")

        baggage = self.generate_baggage_delivery_data()
        self.save_to_parquet(baggage, "baggage_delivery.parquet")

        slot = self.generate_slot_adherence_data()
        self.save_to_parquet(slot, "slot_adherence.parquet")

        safety = self.generate_safety_data()
        self.save_to_parquet(safety, "safety_issues.parquet")
        print("✓ Operational KPI data generation complete\n")


if __name__ == "__main__":
    generator = OperationalKPIDataGenerator()
    generator.generate_all()
