"""
Master script to generate all mock data for the dashboard
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from passenger_data import PassengerDataGenerator
from atm_data import ATMDataGenerator
from queue_time_data import QueueTimeDataGenerator
from security_data import SecurityDataGenerator
from baggage_gate_data import BaggageGateDataGenerator
from biometric_voc_data import BiometricVOCDataGenerator


def generate_all_mock_data():
    """Generate all mock data for BIAL Operations Dashboard"""

    print("="*60)
    print("BIAL AIRPORT OPERATIONS DASHBOARD - MOCK DATA GENERATION")
    print("="*60)
    print()

    # Generate all datasets
    generators = [
        PassengerDataGenerator(),
        ATMDataGenerator(),
        QueueTimeDataGenerator(),
        SecurityDataGenerator(),
        BaggageGateDataGenerator(),
        BiometricVOCDataGenerator()
    ]

    for generator in generators:
        generator.generate_all()

    print("="*60)
    print("✓ ALL MOCK DATA GENERATED SUCCESSFULLY!")
    print("="*60)
    print()
    print("Generated files are located in: data/generated/")
    print()


if __name__ == "__main__":
    generate_all_mock_data()
