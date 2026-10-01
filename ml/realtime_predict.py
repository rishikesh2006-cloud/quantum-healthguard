"""
Quantum HealthGuard — Real-Time Predictive AI Service
Listens to live telemetry stream (healthguard/vitals), feeds normalized features
into Classical Random Forest & Qiskit Quantum QSVC models, and triggers real-time alerts.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import pickle
import numpy as np
import paho.mqtt.client as mqtt
import logging

import config
from alerts.notifier import send_emergency_alert

# Fix Windows console encoding for Python 3.13+
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_DIR / "predict.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("AIPredictor")

# Load Classical Model
RF_MODEL = None
if config.MODEL_PATH.exists():
    try:
        with open(config.MODEL_PATH, "rb") as f:
            RF_MODEL = pickle.load(f)
        log.info(f"Loaded Classical Random Forest Model from {config.MODEL_PATH}")
    except Exception as e:
        log.warning(f"Could not load Random Forest model: {e}")

# Load Quantum QSVC Model
QSVC_MODEL = None
QSVC_PATH = config.ROOT_DIR / "ml" / "qsvc_model.pkl"
if QSVC_PATH.exists():
    try:
        with open(QSVC_PATH, "rb") as f:
            QSVC_MODEL = pickle.load(f)
        log.info(f"Loaded Qiskit QSVC Model from {QSVC_PATH}")
    except Exception as e:
        log.warning(f"Could not load QSVC model: {e}")


def predict_realtime_vitals(vital_data: dict):
    hr = vital_data.get("heart_rate", 72.0)
    spo2 = vital_data.get("spo2", 98.0)
    temp = vital_data.get("temperature", 36.6)
    patient_id = vital_data.get("patient_id", config.DEFAULT_PATIENT_ID)

    features = np.array([[hr, spo2, temp]])
    predictions = {}

    # 1. Classical Random Forest Prediction
    if RF_MODEL:
        try:
            scaled_rf = RF_MODEL["scaler"].transform(features)
            rf_pred_idx = RF_MODEL["model"].predict(scaled_rf)[0]
            rf_label = RF_MODEL["label_encoder"].inverse_transform([rf_pred_idx])[0]
            predictions["RandomForest"] = rf_label
        except Exception as e:
            log.error(f"Random Forest prediction error: {e}")

    # 2. Qiskit Quantum QSVC Prediction
    if QSVC_MODEL:
        try:
            scaled_qsvc = QSVC_MODEL["scaler"].transform(features)
            qsvc_pred_idx = QSVC_MODEL["model"].predict(scaled_qsvc)[0]
            qsvc_label = QSVC_MODEL["label_encoder"].inverse_transform([qsvc_pred_idx])[0]
            predictions["QSVC_Quantum"] = qsvc_label
        except Exception as e:
            log.error(f"QSVC Quantum prediction error: {e}")

    # Output Real-time prediction status
    rf_res = predictions.get("RandomForest", "N/A")
    q_res  = predictions.get("QSVC_Quantum", "N/A")
    log.info(f"[PREDICT] HR={hr:5.1f} | SpO2={spo2:5.1f}% | Temp={temp:5.2f}°C -> RF: {rf_res} | Qiskit QSVC: {q_res}")

    # Trigger emergency alert if any model predicts HIGH_RISK
    if rf_res == "HIGH_RISK" or q_res == "HIGH_RISK":
        send_emergency_alert(
            patient_id=patient_id,
            risk_level="HIGH_RISK",
            vital_data=vital_data,
            model_source=f"RF:{rf_res}|QSVC:{q_res}"
        )


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        log.info(f"Connected to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")
        client.subscribe(config.MQTT_TOPICS["vitals"])
        log.info(f"Subscribed for real-time inference: {config.MQTT_TOPICS['vitals']}")
    else:
        log.error(f"Connection failed (code {rc})")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        predict_realtime_vitals(payload)
    except Exception as e:
        log.error(f"Message parsing error: {e}")


def start_predictor_service():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    log.info(f"Starting Real-Time Predictive AI Service ({config.MQTT_BROKER}:{config.MQTT_PORT})...")
    client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    start_predictor_service()
