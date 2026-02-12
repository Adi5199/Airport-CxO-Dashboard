"""
Passenger volume and show-up profile data generator
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from base_generator import BaseDataGenerator


class PassengerDataGenerator(BaseDataGenerator):
    """Generate passenger volume and show-up profile data"""

    def __init__(self):
        super().__init__()
        self.terminals = self.config['airport']['terminals']
        self.airlines_domestic = self.config['operations']['airlines']['domestic']
        self.airlines_international = self.config['operations']['airlines']['international']

    def generate_daily_pax_volumes(self) -> pd.DataFrame:
        """
        Generate daily passenger volumes by terminal, flow, and type
        """
        dates = self.generate_date_range()
        records = []

        for date in dates:
            # Day of week affects volume
            dow = date.dayofweek
            is_weekend = dow >= 5
            weekend_multiplier = 1.3 if is_weekend else 1.0

            # T1 - Domestic only
            t1_domestic_dep = int(np.random.normal(8000, 800) * weekend_multiplier)
            t1_domestic_arr = int(np.random.normal(7800, 750) * weekend_multiplier)

            # T2 - Mixed (Domestic + International)
            t2_domestic_dep = int(np.random.normal(5000, 600) * weekend_multiplier)
            t2_domestic_arr = int(np.random.normal(4900, 580) * weekend_multiplier)
            t2_intl_dep = int(np.random.normal(3500, 400) * weekend_multiplier)
            t2_intl_arr = int(np.random.normal(3400, 390) * weekend_multiplier)

            # Add records
            records.extend([
                {
                    'date': date,
                    'terminal': 'T1',
                    'flow': 'Departure',
                    'passenger_type': 'Domestic',
                    'pax_count': t1_domestic_dep
                },
                {
                    'date': date,
                    'terminal': 'T1',
                    'flow': 'Arrival',
                    'passenger_type': 'Domestic',
                    'pax_count': t1_domestic_arr
                },
                {
                    'date': date,
                    'terminal': 'T2',
                    'flow': 'Departure',
                    'passenger_type': 'Domestic',
                    'pax_count': t2_domestic_dep
                },
                {
                    'date': date,
                    'terminal': 'T2',
                    'flow': 'Arrival',
                    'passenger_type': 'Domestic',
                    'pax_count': t2_domestic_arr
                },
                {
                    'date': date,
                    'terminal': 'T2',
                    'flow': 'Departure',
                    'passenger_type': 'International',
                    'pax_count': t2_intl_dep
                },
                {
                    'date': date,
                    'terminal': 'T2',
                    'flow': 'Arrival',
                    'passenger_type': 'International',
                    'pax_count': t2_intl_arr
                }
            ])

        df = pd.DataFrame(records)

        # Calculate 7-day averages
        df = df.sort_values(['terminal', 'flow', 'passenger_type', 'date'])
        df = df.groupby(['terminal', 'flow', 'passenger_type'], group_keys=False).apply(
            lambda x: self.calculate_7day_average(x, 'pax_count')
        ).reset_index(drop=True)

        return df

    def generate_hourly_showup_profiles(self) -> pd.DataFrame:
        """
        Generate hourly show-up profiles for departures (entry and PESC)
        """
        dates = self.generate_date_range()
        records = []

        for date in dates:
            dow = date.dayofweek
            is_weekend = dow >= 5
            weekend_mult = 1.3 if is_weekend else 1.0

            # T1 Domestic Departure Entry
            t1_base = int(8000 * weekend_mult)
            t1_hourly = self.generate_hourly_profile(
                date, t1_base,
                peak_hours=[(6, 2.2), (7, 2.5), (8, 2.0), (14, 1.5), (18, 1.8), (19, 2.0)]
            )
            t1_hourly['terminal'] = 'T1'
            t1_hourly['passenger_type'] = 'Domestic'
            t1_hourly['checkpoint'] = 'Departure_Entry'
            t1_hourly['date'] = date
            records.append(t1_hourly)

            # T2 Domestic Departure Entry
            t2_dom_base = int(5000 * weekend_mult)
            t2_dom_hourly = self.generate_hourly_profile(
                date, t2_dom_base,
                peak_hours=[(7, 2.0), (8, 2.3), (9, 1.8), (15, 1.6), (19, 2.1)]
            )
            t2_dom_hourly['terminal'] = 'T2'
            t2_dom_hourly['passenger_type'] = 'Domestic'
            t2_dom_hourly['checkpoint'] = 'Departure_Entry'
            t2_dom_hourly['date'] = date
            records.append(t2_dom_hourly)

            # T2 International Departure Entry
            t2_intl_base = int(3500 * weekend_mult)
            t2_intl_hourly = self.generate_hourly_profile(
                date, t2_intl_base,
                peak_hours=[(5, 1.8), (6, 2.0), (7, 1.9), (13, 1.4), (22, 1.6), (23, 1.5)]
            )
            t2_intl_hourly['terminal'] = 'T2'
            t2_intl_hourly['passenger_type'] = 'International'
            t2_intl_hourly['checkpoint'] = 'Departure_Entry'
            t2_intl_hourly['date'] = date
            records.append(t2_intl_hourly)

        df = pd.concat(records, ignore_index=True)

        # Inject demo anomaly on report date at 14:00-16:00 (for use case)
        if self.report_date in dates:
            # Spike at T2 around 14:00-16:00
            for hour in [14, 15, 16]:
                df = self.add_anomaly(
                    df, self.report_date, hour,
                    'volume', 'spike', magnitude=0.45
                )

        return df

    def generate_pax_by_airline(self) -> pd.DataFrame:
        """
        Generate passenger distribution by airline
        """
        dates = self.generate_date_range()
        records = []

        for date in dates:
            dow = date.dayofweek
            is_weekend = dow >= 5
            weekend_mult = 1.3 if is_weekend else 1.0

            # Domestic airlines market share (T1 + T2)
            total_domestic = int((8000 + 5000) * weekend_mult)
            domestic_shares = {
                'IndiGo': 0.45,
                'Air India': 0.25,
                'SpiceJet': 0.12,
                'Vistara': 0.10,
                'AirAsia India': 0.05,
                'Go First': 0.03
            }

            for airline, share in domestic_shares.items():
                pax = int(total_domestic * share * np.random.uniform(0.95, 1.05))
                records.append({
                    'date': date,
                    'airline': airline,
                    'passenger_type': 'Domestic',
                    'pax_count': pax,
                    'flight_count': int(pax / np.random.uniform(120, 160))
                })

            # International airlines
            total_intl = int(3500 * weekend_mult)
            intl_shares = {
                'Emirates': 0.20,
                'Singapore Airlines': 0.18,
                'British Airways': 0.12,
                'Lufthansa': 0.12,
                'Qatar Airways': 0.15,
                'Thai Airways': 0.10,
                'Air France': 0.13
            }

            for airline, share in intl_shares.items():
                pax = int(total_intl * share * np.random.uniform(0.95, 1.05))
                records.append({
                    'date': date,
                    'airline': airline,
                    'passenger_type': 'International',
                    'pax_count': pax,
                    'flight_count': int(pax / np.random.uniform(180, 250))
                })

        return pd.DataFrame(records)

    def generate_all(self):
        """Generate all passenger-related datasets"""
        print("Generating Passenger Data...")

        # Daily volumes
        daily_pax = self.generate_daily_pax_volumes()
        self.save_to_parquet(daily_pax, 'pax_daily_volumes.parquet')

        # Hourly show-up profiles
        hourly_showup = self.generate_hourly_showup_profiles()
        self.save_to_parquet(hourly_showup, 'pax_hourly_showup.parquet')

        # By airline
        pax_airline = self.generate_pax_by_airline()
        self.save_to_parquet(pax_airline, 'pax_by_airline.parquet')

        print("✓ Passenger data generation complete\n")


if __name__ == "__main__":
    generator = PassengerDataGenerator()
    generator.generate_all()
