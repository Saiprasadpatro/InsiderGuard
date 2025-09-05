import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from .config import RANDOM_SEED


np.random.seed(RANDOM_SEED)


FOLDERS = ["/reports", "/ops", "/training", "/medical", "/finance", "/classified"]
DEVICES = ["desktop", "laptop", "kiosk"]




def generate_users(n_users: int = 20) -> pd.DataFrame:
    users = []
    for i in range(1, n_users + 1):
        uid = f"Soldier{i:02d}"
        base_files = np.random.randint(3, 15)  
        base_data = np.random.uniform(50, 400)
        start_hour = np.random.choice([7, 8, 9, 10])
        end_hour = start_hour + np.random.choice([8, 9])
        users.append({
            "user_id": uid,
            "base_files": base_files,
            "base_data": base_data,
            "work_start": start_hour,
            "work_end": end_hour,
        })
    return pd.DataFrame(users)




def simulate_logs(users: pd.DataFrame, days: int = 21) -> pd.DataFrame:
    rows = []
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(days=days)


    for _, u in users.iterrows():
       current = start
       while current <= now:
           work = np.random.rand() > 0.15 # 85% days worked
           if work:
               files = max(0, int(np.random.normal(u.base_files, 4)))
               data_mb = max(1, np.random.normal(u.base_data, u.base_data * 0.4))
               failed = np.random.poisson(0.8)
               hour = np.random.randint(u.work_start, u.work_end + 1)
               folder = np.random.choice(FOLDERS, p=[.2, .2, .2, .15, .15, .1])
               restricted = folder == "/classified"


# occasional benign night work
               if np.random.rand() < 0.05:
                hour = np.random.choice([0, 1, 2, 3, 4])


# inject rare malicious spikes
               if np.random.rand() < 0.03:
                 files *= np.random.randint(8, 20)
                 data_mb *= np.random.uniform(5, 20)
                 hour = np.random.choice([0, 1, 2, 3])
                 folder = "/classified"
                 restricted = True
                 failed += np.random.randint(3, 10)


               rows.append({
                  "timestamp": current.replace(hour=hour),
                  "date": current.date(),
                  "files_accessed": files,
                  "data_mb": round(float(data_mb), 2),
                  "failed_logins": int(failed),
                  "accessed_folder": folder,
                  "is_restricted": bool(restricted),
                  "device": np.random.choice(DEVICES),
                  "action": np.random.choice(["view", "download", "delete"], p=[.6, .35, .05]),
                  "ip": f"10.0.{np.random.randint(0,255)}.{np.random.randint(1,255)}",
                })
           current += timedelta(days=1)
    df = pd.DataFrame(rows)
    df.sort_values(["timestamp", "user_id"], inplace=True)
    return df