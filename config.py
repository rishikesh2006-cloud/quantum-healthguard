# ──────────────────────────────────────────────────────────────────
#  Quantum HealthGuard — Central Configuration
#  Automatically reads human-editable settings.txt for zero-code changes!
# ──────────────────────────────────────────────────────────────────

import os
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────
ROOT_DIR     = Path(__file__).resolve().parent
SETTINGS_TXT = ROOT_DIR / "settings.txt"
DB_PATH      = ROOT_DIR / "database" / "healthguard.db"
LOG_DIR      = ROOT_DIR / "logs"
MODEL_PATH   = ROOT_DIR / "ml" / "rf_model.pkl"

# Ensure directories exist at import time
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ─── Helper to parse settings.txt ─────────────────────────────────
def load_settings_txt():
    settings = {}
    if SETTINGS_TXT.exists():
        try:
            with open(SETTINGS_TXT, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        settings[k.strip()] = v.strip()
        except Exception as e:
            print(f"[CONFIG WARNING] Could not parse settings.txt: {e}")
    return settings

_st = load_settings_txt()

# ─── Flask Security & Admin Protection ───────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "quantum_healthguard_secret_key_2026")
ADMIN_SECURITY_QUESTION = _st.get("SECURITY_QUESTION", "What is the secret master key for Quantum HealthGuard admin access?")
ADMIN_SECURITY_ANSWER   = _st.get("SECURITY_ANSWER", "healthguard2026")

# ─── MQTT ─────────────────────────────────────────────────────────
MQTT_BROKER = _st.get("MQTT_BROKER", os.getenv("MQTT_BROKER", "localhost"))
MQTT_PORT   = int(_st.get("MQTT_PORT", os.getenv("MQTT_PORT", 1883)))

MQTT_TOPICS = {
    "vitals": "healthguard/vitals",
    "ecg":    "healthguard/ecg",
    "status": "healthguard/status",
    "alerts": "healthguard/alerts",
}

# ─── Dashboard ────────────────────────────────────────────────────
DASHBOARD_HOST = _st.get("HOST", os.getenv("DASHBOARD_HOST", "0.0.0.0"))
DASHBOARD_PORT = int(_st.get("PORT", os.getenv("DASHBOARD_PORT", 5000)))
DASHBOARD_DEBUG = os.getenv("DASHBOARD_DEBUG", "false").lower() == "true"

# ─── Patient / Device ─────────────────────────────────────────────
DEFAULT_PATIENT_ID = _st.get("PATIENT_ID", os.getenv("PATIENT_ID", "P001"))

# ─── Emergency Thresholds (prototype — NOT medical advice) ─────────
THRESHOLDS = {
    "heart_rate": {
        "low":  float(_st.get("HR_LOW", 45)),
        "high": float(_st.get("HR_HIGH", 120))
    },
    "spo2": {
        "critical": float(_st.get("SPO2_CRITICAL", 92)),
        "low": 95.0
    },
    "temperature": {
        "low": 35.0,
        "high": float(_st.get("TEMP_HIGH", 38.5))
    },
}

# ─── Simulator & Performance Load ─────────────────────────────────
SIMULATOR_INTERVAL_SEC = float(_st.get("SIMULATOR_SPEED_SEC", 1.0))
SIMULATOR_ANOMALY_RATE = 0.05  # 5% chance of injecting an anomaly
