import json
from datetime import datetime
import pandas as pd
from pathlib import Path


class AlertManager:
    def __init__(self, path: Path):
        self.path = Path(path)

    def _append(self, record: dict):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def generate(self, logs: pd.DataFrame) -> pd.DataFrame:
        alerts = []

        if logs.empty:
            return pd.DataFrame()

        # Ensure date column
        if "date" not in logs.columns and "timestamp" in logs.columns:
            logs["date"] = pd.to_datetime(logs["timestamp"]).dt.date
        elif "date" in logs.columns:
            logs["date"] = pd.to_datetime(logs["date"])

        for user, group in logs.groupby("user_id"):
            # Case 1: raw logs with 'action'
            if "action" in group.columns:
                failed = (group["action"] == "failed_login").sum()
                restricted = (group["action"] == "access_restricted").sum()
                confidential = (group["action"] == "download_confidential").sum()

            # Case 2: scored data without 'action'
            else:
                failed = int(group.get("failed_logins", pd.Series([0])).sum())
                restricted = int(group.get("restricted_access", pd.Series([0])).sum())
                confidential = int(group.get("confidential_downloads", pd.Series([0])).sum())

            if failed >= 3:
                rec = {
                    "created_at": datetime.utcnow().isoformat(),
                    "user_id": user,
                    "date": str(group["date"].max().date()),
                    "title": "HIGH risk: Multiple failed logins",
                    "description": f"{failed} failed login attempts"
                }
                alerts.append(rec)
                self._append(rec)

            if restricted > 0:
                rec = {
                    "created_at": datetime.utcnow().isoformat(),
                    "user_id": user,
                    "date": str(group["date"].max().date()),
                    "title": "HIGH risk: Restricted access",
                    "description": "User attempted to access restricted resources"
                }
                alerts.append(rec)
                self._append(rec)

            if confidential > 0:
                rec = {
                    "created_at": datetime.utcnow().isoformat(),
                    "user_id": user,
                    "date": str(group["date"].max().date()),
                    "title": "MEDIUM risk: Confidential download",
                    "description": f"{confidential} confidential downloads"
                }
                alerts.append(rec)
                self._append(rec)

        return pd.DataFrame(alerts)
