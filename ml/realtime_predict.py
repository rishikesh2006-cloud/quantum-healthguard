"""
Quantum HealthGuard — Stage 3: Main Analysis Service (Project Laptop)
Receives processed edge data from Raspberry Pi 5 (healthguard/processed) and executes:
  - Primary Algorithm : Quantum Machine Learning — Qiskit Quantum Support Vector Classifier (QSVC)
  - Backup Algorithm  : Classical Machine Learning — Trained Random Forest Classifier
  - Risk-Result Comparison & Fallback Decision Stage:
      * Selects Qiskit QSVC as Primary prediction.
      * Explicitly falls back to Random Forest ONLY if Quantum QSVC analysis is unavailable or fails.
      * Combines ML classification with Stage 2 Edge Safety threshold check for Final Health-Risk Classification.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import sqlite3
import pickle
import numpy as np
import paho.mqtt.client as mqtt
import logging

import config
from alerts.notifier import send_emergency_alert

# Fix Windows console encoding for Python 3.7+
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        getattr(sys.stdout, "reconfigure")(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        getattr(sys.stderr, "reconfigure")(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_DIR / "predict.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("LaptopAIEngine")

# ─── Load Primary Algorithm: Qiskit Quantum QSVC Model ────────────
QSVC_MODEL = None
QSVC_PATH = config.ROOT_DIR / "ml" / "qsvc_model.pkl"
if QSVC_PATH.exists():
    try:
        with open(QSVC_PATH, "rb") as f:
            QSVC_MODEL = pickle.load(f)
        log.info(f"[PRIMARY AI] Loaded Qiskit Quantum QSVC Model from {QSVC_PATH}")
    except Exception as e:
        log.warning(f"[PRIMARY AI] Could not load QSVC model: {e}")

# ─── Load Backup Algorithm: Classical Random Forest Model ─────────
RF_MODEL = None
if config.MODEL_PATH.exists():
    try:
        with open(config.MODEL_PATH, "rb") as f:
            RF_MODEL = pickle.load(f)
        log.info(f"[BACKUP AI]  Loaded Classical Random Forest Model from {config.MODEL_PATH}")
    except Exception as e:
        log.warning(f"[BACKUP AI]  Could not load Random Forest model: {e}")


def update_db_analysis(record_id: int, qsvc_pred: str, rf_pred: str,
                       final_risk: str, decision_source: str, alert_msg: str):
    """Updates the SQLite record with Stage 3 Primary QSVC, Backup RF, and Final Risk Classification."""
    if not record_id:
        return
    try:
        conn = sqlite3.connect(config.DB_PATH)
        conn.execute("""
            UPDATE patient_data
            SET qsvc_pred = ?,
                rf_pred = ?,
                risk_level = ?,
                decision_source = ?,
                alert_msg = ?
            WHERE id = ?
        """, (qsvc_pred, rf_pred, final_risk, decision_source, alert_msg, record_id))
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"Database update error for record #{record_id}: {e}")


def analyze_processed_vitals(vital_data: dict):
    hr         = float(vital_data.get("heart_rate", 72.0))
    spo2       = float(vital_data.get("spo2", 98.0))
    temp       = float(vital_data.get("temperature", 36.6))
    patient_id = vital_data.get("patient_id", config.DEFAULT_PATIENT_ID)
    record_id  = int(vital_data.get("record_id", 0))
    edge_risk  = vital_data.get("edge_risk", "NORMAL")
    edge_reasons = vital_data.get("edge_reasons", [])

    features = np.array([[hr, spo2, temp]])

    # ── 1. Primary Algorithm: Qiskit Quantum QSVC ─────────────────────────
    qsvc_pred = "UNAVAILABLE"
    qsvc_ok   = False
    if QSVC_MODEL is not None:
        try:
            scaled_qsvc   = QSVC_MODEL["scaler"].transform(features)
            qsvc_pred_idx = QSVC_MODEL["model"].predict(scaled_qsvc)[0]
            qsvc_pred     = str(QSVC_MODEL["label_encoder"].inverse_transform([qsvc_pred_idx])[0])
            qsvc_ok       = True
        except Exception as e:
            log.error(f"Primary QSVC Quantum inference error: {e}")
            qsvc_pred = "FAILED"

    # ── 2. Backup Algorithm: Classical Random Forest ──────────────────────
    rf_pred = "UNAVAILABLE"
    rf_ok   = False
    if RF_MODEL is not None:
        try:
            scaled_rf   = RF_MODEL["scaler"].transform(features)
            rf_pred_idx = RF_MODEL["model"].predict(scaled_rf)[0]
            rf_pred     = str(RF_MODEL["label_encoder"].inverse_transform([rf_pred_idx])[0])
            rf_ok       = True
        except Exception as e:
            log.error(f"Backup Random Forest inference error: {e}")
            rf_pred = "FAILED"

    # ── 3. Risk-Result Comparison & Fallback Decision Engine ──────────────
    # Primary Selection: Use Qiskit QSVC if available and valid.
    # Fallback Selection: Fall back to Random Forest ONLY if QSVC is unavailable or fails.
    if qsvc_ok:
        ml_selected_risk = qsvc_pred
        decision_source  = "Primary: Qiskit QSVC"
        if rf_ok and rf_pred == qsvc_pred:
            decision_source = "Primary: Qiskit QSVC (RF Verified)"
    elif rf_ok:
        ml_selected_risk = rf_pred
        decision_source  = "Fallback: Random Forest (QSVC Unavailable)"
    else:
        ml_selected_risk = edge_risk
        decision_source  = "Fallback: Pi 5 Edge Thresholds"

    # Combine with Stage 2 Edge Safety Check (Safety-Critical Priority)
    severity_rank = {"NORMAL": 0, "MODERATE": 1, "HIGH_RISK": 2}
    if severity_rank.get(edge_risk, 0) > severity_rank.get(ml_selected_risk, 0):
        final_risk = edge_risk
        decision_source += " + Edge Safety Override"
    else:
        final_risk = ml_selected_risk

    # Build human-readable clinical alert message
    if final_risk == "HIGH_RISK":
        reason_str = ", ".join(edge_reasons) if edge_reasons else f"AI Pattern ({decision_source})"
        alert_msg = f"CRITICAL ALERT: {reason_str} | QSVC={qsvc_pred}, RF={rf_pred}"
    elif final_risk == "MODERATE":
        alert_msg = f"MODERATE RISK: Borderline vitals detected ({decision_source})"
    else:
        alert_msg = f"NORMAL: Vitals stable ({decision_source})"

    # Persist Stage 3 analysis results into SQLite for Stage 4 Live Dashboard
    update_db_analysis(record_id, qsvc_pred, rf_pred, final_risk, decision_source, alert_msg)

    log.info(
        f"[STAGE 3 AI] #{record_id} HR={hr:5.1f} | SpO2={spo2:5.1f}% | Temp={temp:5.2f}°C -> "
        f"Primary QSVC: {qsvc_pred} | Backup RF: {rf_pred} => FINAL: {final_risk} [{decision_source}]"
    )

    # Trigger emergency alert if Final Risk Classification is HIGH_RISK
    if final_risk == "HIGH_RISK":
        send_emergency_alert(
            patient_id=patient_id,
            risk_level="HIGH_RISK",
            vital_data=vital_data,
            model_source=f"{decision_source} (QSVC:{qsvc_pred}|RF:{rf_pred})"
        )


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        log.info(f"[STAGE 3 AI] Connected to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")
        client.subscribe(config.MQTT_TOPICS["processed"])
        log.info(f"[STAGE 3 AI] Subscribed to Pi 5 Edge processed stream: {config.MQTT_TOPICS['processed']}")
    else:
        log.error(f"Connection failed (code {rc})")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        analyze_processed_vitals(payload)
    except Exception as e:
        log.error(f"Message parsing error: {e}")


def start_predictor_service():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    log.info(f"Starting Stage 3 Laptop Quantum & Classical AI Service ({config.MQTT_BROKER}:{config.MQTT_PORT})...")
    client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    start_predictor_service()
