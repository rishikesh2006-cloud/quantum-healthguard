"""
Quantum HealthGuard — Stage 2: Edge Processing & MQTT Data Receiver (Raspberry Pi 5 Node)
Receives filtered sensor data from ESP32 over Wi-Fi/MQTT, performs advanced edge processing:
  1. Validates incoming data schema and timestamps
  2. Filters noisy, incomplete, or duplicate readings
  3. Checks physiological values against predefined safety thresholds
  4. Detects immediate high-risk conditions (Edge Safety Status)
  5. Temporarily stores readings in SQLite and forwards processed data to Laptop Analysis Engine
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

# Fix Windows console encoding for Python 3.13+
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# ─── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_DIR / "receiver.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("EdgeProcessor")

# Track last seen timestamps per patient for duplicate packet filtering
LAST_PACKET_TIMESTAMPS: dict[str, float] = {}


# ─── Database Initialization & Seamless Schema Migration ──────────
def init_db():
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patient_data (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id      TEXT    NOT NULL,
            timestamp       TEXT    NOT NULL,
            heart_rate      REAL    NOT NULL,
            spo2            REAL    NOT NULL,
            temperature     REAL    NOT NULL,
            risk_level      TEXT    DEFAULT 'NORMAL',
            sensor_status   TEXT    DEFAULT 'ONLINE',
            edge_status     TEXT    DEFAULT 'SAFE',
            qsvc_pred       TEXT    DEFAULT 'PENDING',
            rf_pred         TEXT    DEFAULT 'PENDING',
            decision_source TEXT    DEFAULT 'Edge Pre-Check',
            alert_msg       TEXT    DEFAULT ''
        )
    """)
    # Migrate existing database if columns were added in Stage 2/3/4 architecture upgrade
    existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(patient_data)").fetchall()}
    migrations = [
        ("sensor_status",   "TEXT DEFAULT 'ONLINE'"),
        ("edge_status",     "TEXT DEFAULT 'SAFE'"),
        ("qsvc_pred",       "TEXT DEFAULT 'NORMAL'"),
        ("rf_pred",         "TEXT DEFAULT 'NORMAL'"),
        ("decision_source", "TEXT DEFAULT 'Primary: Qiskit QSVC'"),
        ("alert_msg",       "TEXT DEFAULT ''"),
    ]
    for col_name, col_def in migrations:
        if col_name not in existing_cols:
            conn.execute(f"ALTER TABLE patient_data ADD COLUMN {col_name} {col_def}")
    conn.commit()
    conn.close()
    log.info(f"Edge SQLite Database ready: {config.DB_PATH}")


# ─── Stage 2.1 & 2.2: Data Validation, Noise & Duplicate Filtering ──
def validate_and_filter_edge(data: dict) -> tuple[bool, str]:
    """
    Validates incoming ESP32 packet fields, timestamps, and filters out
    noisy spikes, incomplete packets, or duplicate readings.
    """
    required_fields = ("heart_rate", "spo2", "temperature")
    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Incomplete reading: missing '{field}'"

    try:
        hr   = float(data["heart_rate"])
        spo2 = float(data["spo2"])
        temp = float(data["temperature"])
    except (ValueError, TypeError):
        return False, "Invalid non-numeric physiological value"

    # Physiological noise & spike bounds filter
    if not (20.0 <= hr <= 240.0):
        return False, f"Filtered noisy HR spike ({hr} BPM out of physiological bounds)"
    if not (50.0 <= spo2 <= 100.0):
        return False, f"Filtered noisy SpO2 reading ({spo2}% out of bounds)"
    if not (25.0 <= temp <= 45.0):
        return False, f"Filtered noisy Temperature reading ({temp}°C out of bounds)"

    # Duplicate timestamp check
    patient_id = str(data.get("patient_id", config.DEFAULT_PATIENT_ID))
    pkt_ts = data.get("timestamp")
    if pkt_ts is not None:
        try:
            ts_val = float(pkt_ts)
            if LAST_PACKET_TIMESTAMPS.get(patient_id) == ts_val:
                return False, f"Filtered duplicate packet timestamp ({ts_val})"
            LAST_PACKET_TIMESTAMPS[patient_id] = ts_val
        except (ValueError, TypeError):
            pass

    return True, "VALID"


# ─── Stage 2.3: Edge Safety Threshold Check ───────────────────────
def check_emergency(data: dict) -> tuple[str, str, list[str]]:
    """
    Stage 2 Raspberry Pi 5 Edge Safety Check against predefined thresholds.
    Returns (initial_risk_level, edge_safety_status, [reasons]).
    """
    thr     = config.THRESHOLDS
    hr      = float(data.get("heart_rate", 72.0))
    spo2    = float(data.get("spo2", 98.0))
    temp    = float(data.get("temperature", 36.6))
    reasons = []

    if hr   > thr["heart_rate"]["high"]:  reasons.append(f"HR HIGH ({hr} BPM)")
    if hr   < thr["heart_rate"]["low"]:   reasons.append(f"HR LOW ({hr} BPM)")
    if spo2 < thr["spo2"]["critical"]:    reasons.append(f"SpO2 CRITICAL ({spo2}%)")
    if temp > thr["temperature"]["high"]: reasons.append(f"FEVER ({temp}°C)")
    if temp < thr["temperature"]["low"]:  reasons.append(f"HYPOTHERMIA ({temp}°C)")

    if reasons:
        return "HIGH_RISK", "HIGH_RISK (Threshold Breach)", reasons

    if hr > 100 or spo2 < thr["spo2"]["low"] or temp > 37.5:
        return "MODERATE", "WARNING (Borderline Vitals)", ["Borderline physiological range"]

    return "NORMAL", "SAFE (Within Thresholds)", []


def save_edge_reading(data: dict, risk: str, edge_status: str, alert_msg: str) -> tuple[int, str]:
    utc_now = datetime.now(timezone.utc).isoformat()
    sensor_status = data.get("sensor_status", "ONLINE (ESP32 Wi-Fi/MQTT)")
    conn = sqlite3.connect(config.DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patient_data
            (patient_id, timestamp, heart_rate, spo2, temperature,
             risk_level, sensor_status, edge_status, qsvc_pred, rf_pred, decision_source, alert_msg)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("patient_id", config.DEFAULT_PATIENT_ID),
        utc_now,
        float(data["heart_rate"]),
        float(data["spo2"]),
        float(data["temperature"]),
        risk,
        sensor_status,
        edge_status,
        risk,  # Initial placeholder until Stage 3 AI updates within milliseconds
        risk,
        "Stage 2 Edge Pre-Check",
        alert_msg,
    ))
    record_id = cur.lastrowid or 0
    conn.commit()
    conn.close()
    return record_id, utc_now


# ─── MQTT Callbacks ────────────────────────────────────────────────
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        log.info(f"[STAGE 2 EDGE] Connected to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")
        client.subscribe(config.MQTT_TOPICS["vitals"])
        client.subscribe(config.MQTT_TOPICS["status"])
        log.info(f"[STAGE 2 EDGE] Subscribed to ESP32 stream: {config.MQTT_TOPICS['vitals']}")
    else:
        log.error(f"MQTT connection failed (code {rc})")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        if msg.topic == config.MQTT_TOPICS["vitals"]:
            # Step 1 & 2: Validate and filter noisy/incomplete/duplicate readings
            is_valid, validation_msg = validate_and_filter_edge(payload)
            if not is_valid:
                log.warning(f"[EDGE FILTER DROPPED] {validation_msg}")
                return

            # Step 3: Check physiological values against predefined safety thresholds
            risk, edge_status, reasons = check_emergency(payload)
            alert_msg = ", ".join(reasons) if reasons else "All vitals nominal"

            # Step 4: Temporarily store reading in Edge SQLite DB
            record_id, utc_timestamp = save_edge_reading(payload, risk, edge_status, alert_msg)

            # Step 5: Forward processed data packet to Stage 3 (Project Laptop AI Engine)
            processed_packet = {
                "record_id":     record_id,
                "patient_id":    payload.get("patient_id", config.DEFAULT_PATIENT_ID),
                "heart_rate":    float(payload["heart_rate"]),
                "spo2":          float(payload["spo2"]),
                "temperature":   float(payload["temperature"]),
                "sensor_status": payload.get("sensor_status", "ONLINE (ESP32 Wi-Fi/MQTT)"),
                "edge_status":   edge_status,
                "edge_risk":     risk,
                "edge_reasons":  reasons,
                "timestamp":     utc_timestamp,
            }
            client.publish(config.MQTT_TOPICS["processed"], json.dumps(processed_packet))

            icon = {"NORMAL": "[OK]", "MODERATE": "[WARN]", "HIGH_RISK": "[ALERT]"}.get(risk, "[?]")
            line = (f"{icon} [EDGE:{edge_status.split()[0]:9s}] "
                    f"HR={payload['heart_rate']:5} | "
                    f"SpO2={payload['spo2']:5}% | "
                    f"Temp={payload['temperature']}°C -> Forwarded (#{record_id})")
            if reasons:
                line += f" [{alert_msg}]"
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
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    log.info(f"Starting Stage 2 Raspberry Pi 5 Edge Processor ({config.MQTT_BROKER}:{config.MQTT_PORT})...")
    client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        log.info("Edge Receiver stopped.")
        client.disconnect()
