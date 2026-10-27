"""
Quantum HealthGuard — Automatic USB Serial Bridge
Reads live sensor telemetry directly from ESP32 connected via USB COM port
and republishes it to the local MQTT broker (localhost:1883).
This ensures 100% reliable hardware operation even when Wi-Fi has client isolation!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import logging
import serial
import serial.tools.list_ports
import paho.mqtt.client as mqtt
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SERIAL BRIDGE] %(message)s"
)
log = logging.getLogger("SerialBridge")

def find_esp32_port():
    """Auto-detects ESP32 COM port."""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = (p.description or "").lower()
        if "cp210" in desc or "ch340" in desc or "usb-serial" in desc or "silicon labs" in desc or "com6" in p.device.lower():
            return p.device
    # Fallback to COM6 or first available
    for p in ports:
        if "com" in p.device.lower():
            return p.device
    return "COM6"

def main():
    target_port = os.getenv("ESP32_COM_PORT", find_esp32_port())
    baud_rate = 115200

    log.info(f"Targeting ESP32 Serial Port: {target_port} @ {baud_rate} baud")

    # Connect to local MQTT broker
    client = mqtt.Client()
    try:
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        client.loop_start()
        log.info(f"Connected to local MQTT Broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")
    except Exception as e:
        log.error(f"Cannot connect to MQTT broker: {e}")
        return

    ser = None
    while True:
        try:
            if ser is None or not ser.is_open:
                ser = serial.Serial(target_port, baud_rate, timeout=1)
                log.info(f"Serial port {target_port} OPENED! Streaming live hardware sensor data...")

            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            # Look for JSON payload in serial stream
            if "{" in line and "}" in line:
                start_idx = line.find("{")
                end_idx = line.rfind("}") + 1
                json_str = line[start_idx:end_idx]
                try:
                    payload = json.loads(json_str)
                    if "heart_rate" in payload or "sample" in payload:
                        topic = config.MQTT_TOPICS["ecg"] if "sample" in payload else config.MQTT_TOPICS["vitals"]
                        client.publish(topic, json.dumps(payload))
                        log.info(f"Forwarded from USB: HR={payload.get('heart_rate')} SpO2={payload.get('spo2')}%")
                except json.JSONDecodeError:
                    pass

        except serial.SerialException as e:
            # Port busy (e.g. Arduino IDE Serial Monitor open) or disconnected
            if ser:
                try: ser.close()
                except Exception: pass
            ser = None
            time.sleep(3)
        except Exception as e:
            log.warning(f"Bridge loop warning: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
