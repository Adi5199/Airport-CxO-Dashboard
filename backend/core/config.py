import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent.parent  # Airport CxO Dash/

def load_config():
    with open(BASE_DIR / "config.yaml", "r") as f:
        return yaml.safe_load(f)

CONFIG = load_config()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DATA_DIR = BASE_DIR / "data" / "generated"
