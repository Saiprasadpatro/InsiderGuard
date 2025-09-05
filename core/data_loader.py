import pandas as pd
import os
from core.config import DATA_DIR, LOG_PATH, USER_PATH

def ensure_data_ready(regenerate=False):
    # For now, no regenerate logic — just check files
    if not os.path.exists(LOG_PATH):
        raise FileNotFoundError(f"{LOG_PATH} not found. Place sample_logs.csv in data/ folder.")
    if not os.path.exists(USER_PATH):
        raise FileNotFoundError(f"{USER_PATH} not found. Place seed_users.csv in data/ folder.")

def load_logs(path=LOG_PATH):
    return pd.read_csv(path)

def load_users(path=USER_PATH):
    return pd.read_csv(path)
