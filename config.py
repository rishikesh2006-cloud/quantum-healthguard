# ──────────────────────────────────────────────────────────────────
#  Quantum HealthGuard — Central Configuration
#  Edit this file to change behaviour across the entire project.
#  Copy .env.example → .env and set secrets there (never commit .env)
# ──────────────────────────────────────────────────────────────────

import os
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────
ROOT_DIR   = Path(__file__).resolve().parent
DB_PATH    = ROOT_DIR / "database" / "healthguard.db"
LOG_DIR    = ROOT_DIR / "logs"
MODEL_PATH = ROOT_DIR / "ml" / "rf_model.pkl"

# Ensure directories exist at import time
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ─── MQTT ─────────────────────────────────────────────────────────
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT   = int(os.getenv("MQTT_PORT", 1883))

MQTT_TOPICS = {
    "vitals": "healthguard/vitals",
    "ecg":    "healthguard/ecg",
    "status": "healthguard/status",
    "alerts": "healthguard/alerts",
}

# ─── Dashboard ────────────────────────────────────────────────────
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 5000))
DASHBOARD_DEBUG = os.getenv("DASHBOARD_DEBUG", "false").lower() == "true"

# ─── Patient / Device ─────────────────────────────────────────────
DEFAULT_PATIENT_ID = os.getenv("PATIENT_ID", "P001")

# ─── Emergency Thresholds (prototype — NOT medical advice) ─────────
THRESHOLDS = {
    "heart_rate": {"low": 45,   "high": 120},
    "spo2":       {"critical": 92, "low": 95},
    "temperature":{"low": 35.0, "high": 38.5},
}

# ─── Simulator ────────────────────────────────────────────────────
SIMULATOR_INTERVAL_SEC = 1.0   # seconds between readings
SIMULATOR_ANOMALY_RATE = 0.05  # 5% chance of injecting an anomaly
