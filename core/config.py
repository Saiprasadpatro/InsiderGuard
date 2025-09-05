import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG_PATH = os.path.join(DATA_DIR, "sample_logs.csv")
USER_PATH = os.path.join(DATA_DIR, "seed_users.csv")
ALERTS_PATH = os.path.join(DATA_DIR, "alerts.csv")

RANDOM_SEED = 42
