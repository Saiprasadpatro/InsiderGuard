import os  

USB_LOG_FILE = "data/usb_logs.csv"

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh


from core.config import DATA_DIR, LOG_PATH, ALERTS_PATH, RANDOM_SEED
from core.data_loader import ensure_data_ready, load_logs
from core.features import build_feature_table, build_user_profiles
from core.detector import AnomalyDetector
from core.rules import RuleEngine
from core.risk import RiskScorer
from core.alerts import AlertManager
from core.utils import pretty_time, cache_clear_button
from core.usb_monitor import start_usb_monitor
start_usb_monitor()  # start USB + file monitoring in background

# Auto-refresh every 5 seconds for real-time USB monitoring
st_autorefresh(interval=5000, limit=None, key="usb_refresh")


# ---------------------------
# Streamlit UI setup
# ---------------------------
st.set_page_config(page_title="InsiderGuard", page_icon="🛡️", layout="wide")
st.title("🛡️ InsiderGuard — Insider Threat Monitoring")
st.caption("Software-only: live logs → detection → risk → alerts")

# ---------------------------
# Military Theme (CSS Injection)
# ---------------------------
st.markdown(
    """
    <style>
    /* Background */
    .stApp {
        background-color: #0d1b0d; /* dark green military style */
        color: #e0e0e0;
    }

    /* Titles */
    h1, h2, h3 {
        color: #76c893 !important; /* army green shade */
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1a2d1a;
        color: #e0e0e0;
    }

    /* Buttons */
    button[kind="primary"] {
        background-color: #2e5339;
        color: white;
        border-radius: 6px;
        border: 1px solid #76c893;
    }
    button[kind="primary"]:hover {
        background-color: #76c893;
        color: black;
    }

    /* Dataframes */
    .stDataFrame {
        background-color: #122112;
    }

    /* Alerts styling */
    .stAlert {
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Sidebar actions
with st.sidebar:
    st.header("Controls")
    mode = st.radio(
        "Data source",
        ["Use existing data", "(Re)generate simulated data"],
        index=0
    )
    contamination = st.slider(
        "Model contamination (expected anomaly %)",
        0.01, 0.20, 0.05, 0.01
    )
    train_button = st.button("▶️ Train/Refresh model", use_container_width=True)
    cache_clear_button()

# ---------------------------
# Load / Prepare data
# ---------------------------
ensure_data_ready(regenerate=(mode == "(Re)generate simulated data"))
#logs = load_logs(LOG_PATH)
# Load main logs
logs = load_logs(LOG_PATH)

# Load USB logs if available
if os.path.exists(USB_LOG_FILE):
    usb_logs = pd.read_csv(USB_LOG_FILE)

    # Ensure same schema for merging
    for col in ["date", "user_id", "action", "resource"]:
        if col not in usb_logs.columns:
            usb_logs[col] = "N/A"

    # Merge both logs
    logs = pd.concat([logs, usb_logs], ignore_index=True)


if logs.empty:
    st.error("No logs available. Try regenerating simulated data from the sidebar.")
    st.stop()

# ---------------------------
# Feature engineering
# ---------------------------
features = build_feature_table(logs)
profiles = build_user_profiles(logs)

# ---------------------------
# Anomaly detection
# ---------------------------
if 'detector' not in st.session_state or train_button:
    st.session_state.detector = AnomalyDetector(
        contamination=contamination,
        random_state=RANDOM_SEED
    )
    st.session_state.detector.fit(features)

anomaly_df = st.session_state.detector.score(features)

# ---------------------------
# Rule engine + Risk scoring
# ---------------------------
#rules = RuleEngine(profiles)
#st.info("Tip: tune contamination in the sidebar and retrain to see sensitivity changes.")
#scorer = RiskScorer()
#scored = scorer.score(anomaly_df, rules)
# Rule engine
rules = RuleEngine(profiles)
# evaluate rules against the raw logs to get per-user/day rule flags
rule_flags = rules.evaluate(logs)
st.info("Tip: tune contamination in the sidebar and retrain to see sensitivity changes.")

# Risk scoring (use merge_and_score)
scorer = RiskScorer()
scored = scorer.merge_and_score(anomaly_df, rule_flags)
# Debug: show the first few rows of the scored dataframe
st.write("### Scored head")
st.dataframe(scored.head())



# ---------------------------
# Alerts
# ---------------------------
# Alert manager
alert_manager = AlertManager("data/alerts.jsonl")
alerts = alert_manager.generate(scored)

if not alerts.empty:
    st.error("⚠️ Insider Threat Alerts Detected!")
    st.dataframe(alerts)
else:
    st.success("✅ No insider threats detected.")
    
    # ---------------------------
# USB Alerts (Real-time monitoring)
# ---------------------------
if os.path.exists(USB_LOG_FILE):
    st.subheader("💾 USB Activity Logs")
    usb_logs = pd.read_csv(USB_LOG_FILE)
    st.dataframe(usb_logs.tail(10), use_container_width=True)  # latest 10 entries



# ---------------------------
# (Optional) Show raw logs & scores for debugging
# ---------------------------
with st.expander("📜 Raw Logs"):
    st.dataframe(logs, use_container_width=True)

with st.expander("📊 Risk Scoring Details"):
    st.dataframe(scored, use_container_width=True)
