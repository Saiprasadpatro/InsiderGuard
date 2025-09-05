import pandas as pd


class RuleEngine:
    """Simple, explainable rule checks using user baselines."""

    def __init__(self, profiles: pd.DataFrame):
        self.profiles = profiles.set_index("user_id")

    def evaluate(self, logs: pd.DataFrame) -> pd.DataFrame:
        df = logs.copy()

        # --- Ensure timestamp & hour ---
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['hour'] = df['timestamp'].dt.hour.fillna(0).astype(int)

        # --- Derive features from action column ---
        # If 'action' exists, map it to features
        if 'action' in df.columns:
            df['files_accessed'] = df['action'].apply(
                lambda x: 1 if isinstance(x, str) and ("download" in x or "access" in x) else 0
            )
            df['data_mb'] = df['action'].apply(
                lambda x: 50 if isinstance(x, str) and "download_confidential" in x else 0
            )
            df['is_restricted'] = df['action'].apply(
                lambda x: isinstance(x, str) and "restricted" in x
            )
            df['failed_logins'] = df['action'].apply(
                lambda x: 1 if isinstance(x, str) and x == "failed_login" else 0
            )
        else:
            # If no action column, create safe defaults
            df['files_accessed'] = 0
            df['data_mb'] = 0
            df['is_restricted'] = False
            df['failed_logins'] = 0

        # --- Join baselines (95th percentiles etc.) ---
        df = df.join(self.profiles, on='user_id', how='left')

        # --- Apply rules ---
        flags = []
        for _, r in df.iterrows():
            hits = []

            # R1: Excessive files/data vs user 95th percentile
            if r.get('files_accessed', 0) > 3 * max(1.0, r.get('p95_files', 1.0)):
                hits.append('R1: file spike')

            # R2: Data spike
            if r.get('data_mb', 0) > 4 * max(1.0, r.get('p95_data', 1.0)):
                hits.append('R2: data spike')

            # R3: Night-time activity outside typical window
            if r['hour'] < max(0, r.get('min_hour', 6)) - 1 or r['hour'] > min(23, r.get('max_hour', 20)) + 1:
                hits.append('R3: off-hours login')

            # R4: Classified folder access unusual
            if r.get('is_restricted', False) and r.get('restricted_rate', 0.0) < 0.05:
                hits.append('R4: rare classified access')

            # R5: Many failed logins
            if r.get('failed_logins', 0) >= 5:
                hits.append('R5: failed logins >=5')

            flags.append({
                'timestamp': r.get('timestamp'),
                'date': r.get('date'),
                'user_id': r.get('user_id'),
                'rule_hits': hits,
                'rule_hit_count': len(hits)
            })

        return pd.DataFrame(flags)
