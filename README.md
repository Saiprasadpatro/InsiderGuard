# InsiderGuard

InsiderGuard is a production ready project that detects **insider threats** using ingested real logs, **unsupervised anomaly detection** (IsolationForest), **explainable rule checks**, **risk scoring**, and a **Streamlit dashboard**.

## ⭐ Features

- Real-time ingestion and analysis of defense-style user activity logs
- Per-user baselines & feature engineering
- Anomaly detection (IsolationForest + z-score features)
- Rule engine (file/data spikes, off-hours logins, restricted access, failed logins)
- Risk scoring (LOW/MEDIUM/HIGH)
- Alert generation and UI drilldowns
- 100% software-only (no hardware)

## 🧱 Tech Stack

- **Python 3.10+**
- **Streamlit** (dashboard)
- **scikit-learn**, **pandas**, **numpy**

## 📦 Setup

```bash
# 1) Clone your repo (or copy these files)
# 2) Create & activate a venv (recommended)
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate


# 3) Install dependencies
pip install -r requirements.txt


# 4) Run the app
streamlit run app.py
```

## 🗂 Project Structure

```
app.py # Streamlit UI (entrypoint)
requirements.txt # Dependencies
core/ # Logic modules
config.py # Paths & constants
data_simulator.py # Users + logs generator
data_loader.py # Ensure/load data files
features.py # Aggregations & feature engineering
detector.py # IsolationForest wrapper
rules.py # Explainable rule checks
risk.py # Risk aggregation
alerts.py # Alerts persistence
utils.py # UI helpers
data/
seed_users.csv # Generated on first run
sample_logs.csv # Simulated logs
usb_logs.csv #Live USB Events logs

```

## 🔁 Typical Demo Flow

1. Open the app → sidebar: choose **Use existing** or **(Re)generate** data.
2. Click **Train/Refresh model** to fit IsolationForest.
3. View **Risk Overview**, **Alerts**, and **User Drilldowns**.
4. Tweak **contamination** to adjust sensitivity.

## 🧪 Bring Your Own Data (optional)

Replace `data/sample_logs.csv` with your own logs having these columns:

```
timestamp,date,user_id,files_accessed,data_mb,failed_logins,accessed_folder,is_restricted,device,action,ip
```

- `timestamp`: ISO or parseable datetime (UTC recommended)
- `date`: YYYY-MM-DD (will be parsed if string)
- `is_restricted`: boolean (true/false or 0/1)

## 🔒 Notes

- This is a **demo/prototype** for hackathon use. For production, add authentication, RBAC, secure storage, and proper MLOps.

## 🧑‍💻 Author & License

- Sai Prasad Patro
- License: MIT
