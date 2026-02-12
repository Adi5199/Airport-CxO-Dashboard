"""
Biometric adoption and Voice of Customer (VOC) data generator
"""
import pandas as pd
import numpy as np
from base_generator import BaseDataGenerator


class BiometricVOCDataGenerator(BaseDataGenerator):
    """Generate biometric and VOC data"""

    def generate_biometric_adoption(self) -> pd.DataFrame:
        """Generate biometric adoption metrics"""
        dates = self.generate_date_range()
        records = []

        channels = self.config['operations']['biometric_channels']

        for date in dates:
            for terminal in ['T1', 'T2']:
                # Total eligible passengers
                if terminal == 'T1':
                    total_pax = int(np.random.normal(8000, 800))
                else:
                    total_pax = int(np.random.normal(8500, 900))

                # Adoption rate trending upward over time
                days_from_start = (date - self.start_date).days
                base_adoption = 35 + (days_from_start * 0.3)  # Growing adoption
                adoption_pct = min(65, base_adoption + np.random.uniform(-3, 3))

                biometric_pax = int(total_pax * (adoption_pct / 100))

                # Channel distribution
                channel_dist = {
                    'Digi Yatra App': 0.45,
                    'Kiosk': 0.35,
                    'DOT (Digital on Terminal)': 0.20
                }

                for channel, share in channel_dist.items():
                    channel_pax = int(biometric_pax * share)
                    successful = int(channel_pax * np.random.uniform(0.92, 0.98))

                    records.append({
                        'date': date,
                        'terminal': terminal,
                        'channel': channel,
                        'total_eligible_pax': total_pax,
                        'biometric_registrations': channel_pax,
                        'successful_boardings': successful,
                        'success_rate_pct': round((successful / channel_pax * 100) if channel_pax > 0 else 0, 2),
                        'adoption_pct': round(adoption_pct, 2)
                    })

        return pd.DataFrame(records)

    def generate_voc_feedback(self) -> pd.DataFrame:
        """Generate Voice of Customer feedback data"""
        dates = self.generate_date_range()
        records = []

        departments = self.config['operations']['departments']
        media_types = self.config['operations']['voc_media_types']

        for date in dates:
            for terminal in ['T1', 'T2', 'Overall']:
                for dept in departments if terminal == 'Overall' else [None]:
                    # Compliments and complaints
                    complaints = int(np.random.normal(12, 4))
                    compliments = int(np.random.normal(20, 6))

                    # Media type distribution
                    total_feedback = complaints + compliments
                    for media in media_types:
                        media_share = np.random.uniform(0.1, 0.3)
                        count = int(total_feedback * media_share)

                        records.append({
                            'date': date,
                            'terminal': terminal,
                            'department': dept if terminal == 'Overall' else 'All',
                            'media_type': media,
                            'complaints': int(count * (complaints / total_feedback)),
                            'compliments': int(count * (compliments / total_feedback))
                        })

        df = pd.DataFrame(records)

        # Calculate ratios
        df['total_feedback'] = df['complaints'] + df['compliments']
        df['compliments_to_complaints_ratio'] = (
            df['compliments'] / df['complaints'].replace(0, 1)
        ).round(2)

        # Inject anomaly - more complaints on report_date
        mask = (df['date'] == self.report_date) & (df['terminal'] == 'T2')
        df.loc[mask, 'complaints'] = (df.loc[mask, 'complaints'] * 1.6).astype(int)
        df.loc[mask, 'compliments_to_complaints_ratio'] = (
            df.loc[mask, 'compliments'] / df.loc[mask, 'complaints'].replace(0, 1)
        ).round(2)

        return df

    def generate_voc_messages(self) -> pd.DataFrame:
        """Generate sample customer messages (sanitized)"""
        templates = {
            'positive': [
                "Quick security clearance today. Great job!",
                "Loved the smooth check-in experience.",
                "Biometric boarding was seamless and fast.",
                "Clean facilities and helpful staff.",
                "Efficient baggage delivery. Thank you!"
            ],
            'negative': [
                "Long queue at security. Waited over 20 minutes.",
                "Check-in counters were understaffed during peak hours.",
                "Confusion at departure entry. Needs better signage.",
                "Baggage took too long to arrive at the belt.",
                "Too many rejections at security screening."
            ]
        }

        dates = self.generate_date_range()
        records = []

        for date in dates:
            # Random messages for the day
            num_messages = np.random.randint(5, 15)
            for _ in range(num_messages):
                sentiment = np.random.choice(['positive', 'negative'], p=[0.65, 0.35])
                message = np.random.choice(templates[sentiment])
                terminal = np.random.choice(['T1', 'T2'])
                dept = np.random.choice(self.config['operations']['departments'])

                records.append({
                    'date': date,
                    'terminal': terminal,
                    'department': dept,
                    'sentiment': sentiment,
                    'message': message,
                    'media': np.random.choice(self.config['operations']['voc_media_types'])
                })

        df = pd.DataFrame(records)

        # More negative messages on report_date related to queues
        report_messages = [
            "Extremely long wait at T2 security this afternoon.",
            "Check-in queues were terrible around 2-3 PM.",
            "Missed flight due to security delays. Very frustrated.",
            "Why so many rejections at Lane 6? Causes huge delays."
        ]

        for msg in report_messages:
            records.append({
                'date': self.report_date,
                'terminal': 'T2',
                'department': np.random.choice(['Security', 'Customer Service']),
                'sentiment': 'negative',
                'message': msg,
                'media': np.random.choice(['Email', 'Phone Call', 'Chatbot'])
            })

        return pd.DataFrame(records)

    def generate_all(self):
        print("Generating Biometric & VOC Data...")

        biometric = self.generate_biometric_adoption()
        self.save_to_parquet(biometric, 'biometric_adoption.parquet')

        voc_feedback = self.generate_voc_feedback()
        self.save_to_parquet(voc_feedback, 'voc_feedback.parquet')

        voc_messages = self.generate_voc_messages()
        self.save_to_parquet(voc_messages, 'voc_messages.parquet')

        print("✓ Biometric & VOC data generation complete\n")


if __name__ == "__main__":
    generator = BiometricVOCDataGenerator()
    generator.generate_all()
