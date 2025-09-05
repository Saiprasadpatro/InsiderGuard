import pandas as pd
import streamlit as st


class RiskScorer:
    def merge_and_score(self, anomaly_df: pd.DataFrame, rule_flags: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
        # Aggregate rule flags: combine hits per user/day
        r = rule_flags.groupby(['user_id', 'date']).agg(
            rule_hits=("rule_hits", lambda lists: sum(lists, [])),
            rule_hit_count=("rule_hit_count", "sum")
        ).reset_index()

        if debug:
            st.write("### Rule flags aggregated")
            st.dataframe(r.head())

        # Merge with anomaly scores
        df = anomaly_df.merge(r, on=["user_id", "date"], how="left")

        # Handle missing values safely
        df["rule_hits"] = df["rule_hits"].apply(lambda x: x if isinstance(x, list) else [])
        df["rule_hit_count"] = df["rule_hit_count"].fillna(0).astype(int)

        if debug:
            st.write("### After merge (with anomaly scores)")
            st.dataframe(df.head())

        # Risk score: 70% anomaly + 30% rule density (clipped)
        df["risk_score"] = (
            0.7 * df["anomaly_score"]
            + 0.3 * (df["rule_hit_count"].clip(0, 6) / 6)
        )

        # Risk level labels
        def label(x):
            if x >= 0.75:
                return "HIGH"
            if x >= 0.45:
                return "MEDIUM"
            return "LOW"

        df["risk_level"] = df["risk_score"].apply(label)

        if debug:
            st.write("### Final scored dataframe")
            st.dataframe(df.head())

        return df
