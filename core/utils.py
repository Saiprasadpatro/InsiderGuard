import pandas as pd
import random
from datetime import datetime, timedelta
import os
import streamlit as st

DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "sample_logs.csv")
USER_FILE = os.path.join(DATA_DIR, "seed_users.csv")



def cache_clear_button():
    """Adds a button in sidebar to clear Streamlit cache"""
    if st.sidebar.button("🔄 Clear Cache"):
        st.cache_data.clear()
        st.sidebar.success("Cache cleared!")


def pretty_time(date_str):
    """Format YYYY-MM-DD into a human-readable date"""
    try:
        from datetime import datetime
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return date_str


def generate_dummy_logs(n=50):
    actions = ["login", "logout", "download", "upload", "delete", "access"]
    users = [f"user{i}" for i in range(1, 6)]
    resources = ["server1", "server2", "database", "file1", "file2"]

    data = []
    today = datetime.today()

    for _ in range(n):
        entry = {
            "date": (today - timedelta(days=random.randint(0, 10))).strftime("%Y-%m-%d"),
            "user_id": random.choice(users),
            "action": random.choice(actions),
            "resource": random.choice(resources),
        }
        data.append(entry)

    df = pd.DataFrame(data)

    # Ensure the data folder exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Save to data/sample_logs.csv
    df.to_csv(LOG_FILE, index=False)
    print(f"✅ Dummy logs saved to {LOG_FILE}")


def load_logs():
    """Load logs from data/sample_logs.csv"""
    if not os.path.exists(LOG_FILE):
        print("⚠️ No log file found. Generating dummy logs...")
        generate_dummy_logs()

    logs = pd.read_csv(LOG_FILE)

    # Safety check for 'date' column
    if "date" not in logs.columns:
        raise KeyError("❌ 'date' column missing in logs. Please regenerate dummy data.")

    return logs


def load_users():
    """Load users from data/seed_users.csv"""
    if not os.path.exists(USER_FILE):
        raise FileNotFoundError(f"⚠️ {USER_FILE} not found!")

    return pd.read_csv(USER_FILE)
