import pandas as pd
import numpy as np

def build_feature_table(logs: pd.DataFrame) -> pd.DataFrame:
    # Ensure timestamp is datetime and extract date
    logs = logs.copy()
    logs["timestamp"] = pd.to_datetime(logs["timestamp"])
    logs["date"] = logs["timestamp"].dt.date

    # Create derived event counts
    logs["files_accessed"] = logs["action"].apply(lambda x: 1 if x in ["download", "upload", "open"] else 0)
    logs["failed_logins"] = logs["action"].apply(lambda x: 1 if x == "failed_login" else 0)
    logs["is_restricted"] = logs["action"].apply(lambda x: 1 if x == "restricted_access" else 0)

    # Simulated data_mb for download/upload (just placeholder)
    logs["data_mb"] = logs["action"].apply(lambda x: np.random.randint(1, 50) if x in ["download", "upload"] else 0)

    # Aggregate per user per day
    grp = logs.groupby(["user_id", "date"]).agg(
        files_accessed=("files_accessed", "sum"),
        data_mb=("data_mb", "sum"),
        failed_logins=("failed_logins", "sum"),
        night_ops=("timestamp", lambda s: int(((s.dt.hour < 6) | (s.dt.hour > 22)).any())),
        restricted_hits=("is_restricted", "sum"),
    ).reset_index()

    # Normalized features
    grp["files_per_mb"] = grp["files_accessed"] / (grp["data_mb"] + 1e-6)
    for col in ["files_accessed", "data_mb", "failed_logins"]:
        grp[f"z_{col}"] = (grp[col] - grp[col].mean()) / (grp[col].std() + 1e-6)

    return grp


def build_user_profiles(logs: pd.DataFrame) -> pd.DataFrame:
    logs = logs.copy()
    logs["timestamp"] = pd.to_datetime(logs["timestamp"])
    logs["hour"] = logs["timestamp"].dt.hour

    logs["files_accessed"] = logs["action"].apply(lambda x: 1 if x in ["download", "upload", "open"] else 0)
    logs["data_mb"] = logs["action"].apply(lambda x: np.random.randint(1, 50) if x in ["download", "upload"] else 0)
    logs["is_restricted"] = logs["action"].apply(lambda x: 1 if x == "restricted_access" else 0)

    prof = logs.groupby("user_id").agg(
        avg_files=("files_accessed", "mean"),
        avg_data_mb=("data_mb", "mean"),
        p95_files=("files_accessed", lambda s: float(np.percentile(s, 95))),
        p95_data=("data_mb", lambda s: float(np.percentile(s, 95))),
        min_hour=("hour", "min"),
        max_hour=("hour", "max"),
        restricted_rate=("is_restricted", "mean"),
    ).reset_index()

    prof["login_window"] = prof.apply(lambda r: f"{int(r.min_hour)}:00–{int(r.max_hour)}:00", axis=1)
    return prof
