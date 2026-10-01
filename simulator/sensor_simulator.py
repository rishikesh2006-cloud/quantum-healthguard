"""
Quantum HealthGuard — Sensor Simulator
Simulates ESP32 + MAX30102 + AD8232 + Temperature Sensor
Publishes realistic (with occasional anomalies) data to MQTT broker.

This module REPLACES hardware during development/testing.
When real hardware arrives, only this file needs to change.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paho.mqtt.client as mqtt
import json
import time
import random
import math
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

# ─── MQTT Setup ───────────────────────────────────────────────────
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    client = mqtt.Client()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[SIM] Connected to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")
    else:
        print(f"[SIM] Connection failed (code {rc}). Is the broker running?")
        sys.exit(1)

client.on_connect = on_connect
client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.loop_start()


# ─── Simulation Logic ─────────────────────────────────────────────
def simulate_vitals(t):
    """Simulate realistic biosensor readings with occasional anomalies."""
    thr = config.THRESHOLDS
    hr   = 72 + 5 * math.sin(t / 10) + random.gauss(0, 2)
    spo2 = 97.5 + random.gauss(0, 0.3)
    temp = 36.6 + random.gauss(0, 0.1)

    if random.random() < config.SIMULATOR_ANOMALY_RATE:
        anomaly = random.choice(["high_hr", "low_hr", "low_spo2", "high_temp"])
        if anomaly == "high_hr":
            hr = random.uniform(thr["heart_rate"]["high"] + 5, 145)
        elif anomaly == "low_hr":
            hr = random.uniform(30, thr["heart_rate"]["low"] - 1)
        elif anomaly == "low_spo2":
            spo2 = random.uniform(85, thr["spo2"]["critical"] - 1)
        elif anomaly == "high_temp":
            temp = random.uniform(thr["temperature"]["high"] + 0.5, 40.5)

    return {
        "patient_id":  config.DEFAULT_PATIENT_ID,
        "heart_rate":  round(hr, 1),
        "spo2":        round(min(max(spo2, 80), 100), 1),
        "temperature": round(temp, 2),
        "timestamp":   time.time(),
    }


def simulate_ecg(t):
    """Generate a simplified ECG-like waveform sample."""
    phase  = t % 1.0
    sample = 512
    sample += int(30  * math.exp(-((phase - 0.10) ** 2) / 0.0020))
    sample += int(200 * math.exp(-((phase - 0.30) ** 2) / 0.0005))
    sample -= int(60  * math.exp(-((phase - 0.35) ** 2) / 0.0010))
    sample += int(40  * math.exp(-((phase - 0.55) ** 2) / 0.0050))
    return {"sample": max(0, min(1023, sample)), "timestamp": time.time()}


# ─── Main Loop ────────────────────────────────────────────────────
if __name__ == "__main__":
    time.sleep(1)  # let MQTT connect

    t    = 0.0
    step = config.SIMULATOR_INTERVAL_SEC

    print("=" * 55)
    print("  Quantum HealthGuard -- Sensor Simulator")
    print(f"  Publishing to {config.MQTT_BROKER}:{config.MQTT_PORT}")
    print("  Press Ctrl+C to stop.")
    print("=" * 55)

    try:
        while True:
            vitals = simulate_vitals(t)
            ecg    = simulate_ecg(t)

            client.publish(config.MQTT_TOPICS["vitals"], json.dumps(vitals))
            client.publish(config.MQTT_TOPICS["ecg"],    json.dumps(ecg))

            icon = "[ALERT]" if vitals["heart_rate"] > 120 or vitals["spo2"] < 92 else "[OK]"
            print(f"{icon} HR={vitals['heart_rate']:5.1f} BPM | "
                  f"SpO2={vitals['spo2']:5.1f}% | "
                  f"Temp={vitals['temperature']:5.2f}°C")

            t += step
            time.sleep(step)

    except KeyboardInterrupt:
        print("\n[SIM] Simulator stopped.")
        client.loop_stop()
        client.disconnect()
