"""
Quantum HealthGuard — MQTT Data Receiver
Subscribes to sensor topics, validates data, runs local emergency checks,
and stores readings to SQLite.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paho.mqtt.client as mqtt
import json
import sqlite3
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
import config

# ─── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_DIR / "receiver.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ─── Database ─────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patient_data (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  TEXT    NOT NULL,
            timestamp   TEXT    NOT NULL,
            heart_rate  REAL    NOT NULL,
            spo2        REAL    NOT NULL,
            temperature REAL    NOT NULL,
            risk_level  TEXT    DEFAULT 'UNKNOWN'
        )
    """)
    conn.commit()
    conn.close()
    log.info(f"Database ready → {config.DB_PATH}")


def save_reading(data: dict, risk: str):
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("""
        INSERT INTO patient_data
            (patient_id, timestamp, heart_rate, spo2, temperature, risk_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("patient_id", config.DEFAULT_PATIENT_ID),
        datetime.now(timezone.utc).isoformat(),
        data["heart_rate"],
        data["spo2"],
        data["temperature"],
        risk,
    ))
    conn.commit()
    conn.close()


# ─── Emergency Check ──────────────────────────────────────────────
def check_emergency(data: dict) -> tuple[str, list[str]]:
    """
    Prototype safety check using configured thresholds.
    Returns (risk_level, [reasons]).
    NOT a medical diagnosis.
    """
    thr     = config.THRESHOLDS
    hr      = data.get("heart_rate", 0)
    spo2    = data.get("spo2", 100)
    temp    = data.get("temperature", 37)
    reasons = []

    if hr   > thr["heart_rate"]["high"]:  reasons.append(f"HR HIGH {hr} BPM")
    if hr   < thr["heart_rate"]["low"]:   reasons.append(f"HR LOW {hr} BPM")
    if spo2 < thr["spo2"]["critical"]:    reasons.append(f"SpO2 CRITICAL {spo2}%")
    if temp > thr["temperature"]["high"]: reasons.append(f"FEVER {temp}°C")
    if temp < thr["temperature"]["low"]:  reasons.append(f"HYPOTHERMIA {temp}°C")

    if reasons:
        return "HIGH_RISK", reasons

    if hr > 100 or spo2 < thr["spo2"]["low"] or temp > 37.5:
        return "MODERATE", []

    return "NORMAL", []


# ─── MQTT Callbacks ────────────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log.info(f"Connected to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")
        for topic in config.MQTT_TOPICS.values():
            client.subscribe(topic)
            log.info(f"Subscribed → {topic}")
    else:
        log.error(f"MQTT connection failed (code {rc})")


ICONS = {"NORMAL": "✅", "MODERATE": "⚠️ ", "HIGH_RISK": "🚨"}

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        if msg.topic == config.MQTT_TOPICS["vitals"]:
            risk, reasons = check_emergency(payload)
            save_reading(payload, risk)

            icon = ICONS.get(risk, "❓")
            line = (f"{icon} [{risk:9s}]  "
                    f"HR={payload['heart_rate']:5}  "
                    f"SpO2={payload['spo2']:5}%  "
                    f"Temp={payload['temperature']}°C")
            if reasons:
                line += f"  ⚠ {', '.join(reasons)}"
            log.info(line)

    except json.JSONDecodeError:
        log.warning(f"Invalid JSON on {msg.topic}")
    except KeyError as e:
        log.warning(f"Missing field: {e}")
    except Exception as e:
        log.error(f"Unexpected error: {e}")


# ─── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.on_message = on_message

    log.info(f"Connecting to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT} ...")
    client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        log.info("Receiver stopped.")
        client.disconnect()
