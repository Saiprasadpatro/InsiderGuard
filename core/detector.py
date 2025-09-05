import pandas as pd
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self, contamination=0.05, random_state=42):
        self.contamination = contamination
        self.model = IsolationForest(
             contamination=contamination,
             n_estimators=200,
             random_state=random_state,
         )
        self.feat_cols = [
            "files_accessed",
            "data_mb",
            "failed_logins",
            "night_ops",
            "restricted_hits",
            "files_per_mb",
            "z_files_accessed",
            "z_data_mb",
            "z_failed_logins",
        ]
    def fit(self, features: pd.DataFrame):
        X = features[self.feat_cols].fillna(0)
        self.model.fit(X)


    def score(self, features: pd.DataFrame) -> pd.DataFrame:
        X = features[self.feat_cols].fillna(0)
        scores = -self.model.score_samples(X) # higher = more anomalous
        out = features[["user_id", "date"]].copy()
        out["anomaly_score"] = (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)
        return out   