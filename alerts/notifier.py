"""
Quantum HealthGuard — Emergency Alert Notification Engine
Triggers emergency alerts when critical risk is detected via rules or AI models.
Publishes alerts to MQTT topic healthguard/alerts and logs to system logs.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paho.mqtt.client as mqtt
import json
import time
import logging
from datetime import datetime, timezone
import config

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
        logging.FileHandler(config.LOG_DIR / "alerts.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("AlertEngine")


def send_emergency_alert(patient_id: str, risk_level: str, vital_data: dict, model_source: str = "RuleEngine"):
    """Publishes emergency alert notification payload to MQTT."""
    alert_payload = {
        "event": "EMERGENCY_ALERT",
        "patient_id": patient_id,
        "risk_level": risk_level,
        "source": model_source,
        "vitals": vital_data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    log.warning(f"🚨 [EMERGENCY ALERT] Patient: {patient_id} | Risk: {risk_level} | Source: {model_source}")
    log.warning(f"   Vitals -> HR: {vital_data.get('heart_rate')} BPM | SpO2: {vital_data.get('spo2')}% | Temp: {vital_data.get('temperature')}°C")

    try:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        except AttributeError:
            client = mqtt.Client()
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 10)
        client.publish(config.MQTT_TOPICS["alerts"], json.dumps(alert_payload))
        client.disconnect()
    except Exception as e:
        log.error(f"Failed to publish alert to MQTT broker: {e}")


if __name__ == "__main__":
    send_emergency_alert(
        patient_id="P001",
        risk_level="HIGH_RISK",
        vital_data={"heart_rate": 138.5, "spo2": 88.5, "temperature": 39.4},
        model_source="TestAlert"
    )
