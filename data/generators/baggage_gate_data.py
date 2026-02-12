"""
Baggage reclaim and gate utilization data generator
"""
import pandas as pd
import numpy as np
from base_generator import BaseDataGenerator


class BaggageGateDataGenerator(BaseDataGenerator):
    """Generate baggage and gate utilization data"""

    def generate_baggage_utilization(self) -> pd.DataFrame:
        """Generate baggage belt utilization"""
        dates = self.generate_date_range()
        records = []

        belts = (
            self.config['operations']['terminals']['T1']['baggage_belts'] +
            self.config['operations']['terminals']['T2']['baggage_belts']
        )
        airlines_dom = self.config['operations']['airlines']['domestic']
        airlines_intl = self.config['operations']['airlines']['international']

        for date in dates:
            for belt in belts:
                terminal = 'T1' if belt.startswith('T1') else 'T2'
                is_intl = 'Intl' in belt

                # Flights per belt per day
                flights = int(np.random.normal(12, 3))

                # PAX per belt
                if is_intl:
                    pax_per_belt = int(np.random.normal(2200, 300))
                    airlines = np.random.choice(airlines_intl, 3, replace=False)
                else:
                    pax_per_belt = int(np.random.normal(1600, 250))
                    airlines = np.random.choice(airlines_dom, 3, replace=False)

                # Utilization score (0-100)
                utilization = min(100, (flights / 15) * 100 + np.random.uniform(-5, 5))

                records.append({
                    'date': date,
                    'belt': belt,
                    'terminal': terminal,
                    'belt_type': 'International' if is_intl else 'Domestic',
                    'flights': flights,
                    'pax': pax_per_belt,
                    'pax_per_flight': round(pax_per_belt / flights, 1),
                    'utilization_pct': round(utilization, 1),
                    'primary_airlines': ', '.join(airlines)
                })

        return pd.DataFrame(records)

    def generate_gate_utilization(self) -> pd.DataFrame:
        """Generate gate/stand utilization and boarding mode"""
        dates = self.generate_date_range()
        records = []

        t1_gates = self.config['operations']['terminals']['T1']['gates']
        t2_gates = self.config['operations']['terminals']['T2']['gates']
        all_gates = [(g, 'T1') for g in t1_gates] + [(g, 'T2') for g in t2_gates]

        for date in dates:
            for gate, terminal in all_gates:
                # Aerobridge gates (A-gates, B-gates starting with numbers)
                is_aerobridge = gate.startswith('A') or (gate.startswith('B') and gate[1].isdigit())

                if is_aerobridge:
                    boarding_mode = 'Aerobridge'
                    flights = int(np.random.normal(8, 2))
                    pax = int(np.random.normal(1100, 200))
                else:
                    boarding_mode = 'Bus' if np.random.random() > 0.3 else 'Aerobridge'
                    flights = int(np.random.normal(6, 2))
                    pax = int(np.random.normal(800, 150))

                records.append({
                    'date': date,
                    'gate': gate,
                    'terminal': terminal,
                    'boarding_mode': boarding_mode,
                    'flights': max(1, flights),
                    'pax': pax,
                    'pax_per_flight': round(pax / max(1, flights), 1)
                })

        df = pd.DataFrame(records)

        # Inject anomaly - higher bus boarding on report_date at T2
        mask = (df['date'] == self.report_date) & (df['terminal'] == 'T2')
        df.loc[mask, 'boarding_mode'] = np.where(
            np.random.random(mask.sum()) > 0.4, 'Bus', df.loc[mask, 'boarding_mode']
        )

        return df

    def generate_all(self):
        print("Generating Baggage & Gate Data...")

        baggage = self.generate_baggage_utilization()
        self.save_to_parquet(baggage, 'baggage_utilization.parquet')

        gates = self.generate_gate_utilization()
        self.save_to_parquet(gates, 'gate_utilization.parquet')

        print("✓ Baggage & Gate data generation complete\n")


if __name__ == "__main__":
    generator = BaggageGateDataGenerator()
    generator.generate_all()
