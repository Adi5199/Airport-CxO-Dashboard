"""
Aircraft Traffic Movements (ATM) data generator
"""
import pandas as pd
import numpy as np
from base_generator import BaseDataGenerator


class ATMDataGenerator(BaseDataGenerator):
    """Generate ATM data"""

    def generate_daily_atm(self) -> pd.DataFrame:
        """Generate daily ATM volumes"""
        dates = self.generate_date_range()
        records = []

        for date in dates:
            dow = date.dayofweek
            weekend_mult = 1.2 if dow >= 5 else 1.0

            # T1 Domestic
            t1_dep = int(np.random.normal(55, 5) * weekend_mult)
            t1_arr = int(np.random.normal(54, 5) * weekend_mult)

            # T2 Mixed
            t2_dom_dep = int(np.random.normal(35, 4) * weekend_mult)
            t2_dom_arr = int(np.random.normal(34, 4) * weekend_mult)
            t2_intl_dep = int(np.random.normal(18, 3) * weekend_mult)
            t2_intl_arr = int(np.random.normal(17, 3) * weekend_mult)

            records.extend([
                {'date': date, 'terminal': 'T1', 'flow': 'Departure', 'type': 'Domestic', 'atm_count': t1_dep},
                {'date': date, 'terminal': 'T1', 'flow': 'Arrival', 'type': 'Domestic', 'atm_count': t1_arr},
                {'date': date, 'terminal': 'T2', 'flow': 'Departure', 'type': 'Domestic', 'atm_count': t2_dom_dep},
                {'date': date, 'terminal': 'T2', 'flow': 'Arrival', 'type': 'Domestic', 'atm_count': t2_dom_arr},
                {'date': date, 'terminal': 'T2', 'flow': 'Departure', 'type': 'International', 'atm_count': t2_intl_dep},
                {'date': date, 'terminal': 'T2', 'flow': 'Arrival', 'type': 'International', 'atm_count': t2_intl_arr},
            ])

        df = pd.DataFrame(records)
        df = df.groupby(['terminal', 'flow', 'type'], group_keys=False).apply(
            lambda x: self.calculate_7day_average(x, 'atm_count')
        ).reset_index(drop=True)
        return df

    def generate_all(self):
        print("Generating ATM Data...")
        atm_daily = self.generate_daily_atm()
        self.save_to_parquet(atm_daily, 'atm_daily.parquet')
        print("✓ ATM data generation complete\n")


if __name__ == "__main__":
    generator = ATMDataGenerator()
    generator.generate_all()
