"""
Quantum HealthGuard — Master System Entrypoint
HARDWARE MODE ONLY — No simulator, no random values.
Starts: MQTT Broker, Edge Receiver, Serial Bridge, AI Predictor, Flask Dashboard.
"""

import sys
import os
import time
import subprocess
import socket

if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        getattr(sys.stdout, "reconfigure")(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        getattr(sys.stderr, "reconfigure")(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_BIN = sys.executable

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def start_service(name, script_path):
    print(f"[{name}] Starting {os.path.basename(script_path)}...")
    return subprocess.Popen([PYTHON_BIN, script_path], cwd=ROOT_DIR)

def main():
    lan_ip = get_lan_ip()
    port = 5000

    print("=" * 65)
    print("  QUANTUM HEALTHGUARD — REAL HARDWARE MODE")
    print("  No simulator. No random values. Real sensors only.")
    print("=" * 65)
    print()

    processes = []

    try:
        # 1. Start MQTT Broker
        p_broker = start_service("BROKER", os.path.join(ROOT_DIR, "communication", "mqtt_broker.py"))
        processes.append(("Broker", p_broker))
        time.sleep(2)

        # 2. Start Edge Processor (receives data from ESP32 via MQTT)
        p_recv = start_service("RECEIVER", os.path.join(ROOT_DIR, "communication", "mqtt_receiver.py"))
        processes.append(("Receiver", p_recv))
        time.sleep(2)

        # 3. Start USB Serial Bridge (reads ESP32 COM port directly as backup)
        serial_bridge_path = os.path.join(ROOT_DIR, "communication", "serial_receiver.py")
        if os.path.exists(serial_bridge_path):
            p_serial = start_service("SERIAL_BRIDGE", serial_bridge_path)
            processes.append(("SerialBridge", p_serial))
            time.sleep(2)

        # 4. Start AI Predictor (Quantum QSVC + Random Forest)
        p_pred = start_service("PREDICTOR", os.path.join(ROOT_DIR, "ml", "realtime_predict.py"))
        processes.append(("Predictor", p_pred))
        time.sleep(2)

        print()
        print("=" * 65)
        print("  ALL SERVICES RUNNING — REAL HARDWARE MODE")
        print("  ---------------------------------------------------------")
        print(f"  [MOBILE] Phone / Tablet : http://{lan_ip}:{port}")
        print(f"  [LAPTOP] Local PC       : http://localhost:{port}")
        print(f"  [ADMIN]  Admin Panel    : http://localhost:{port}/admin")
        print("  ---------------------------------------------------------")
        print("  Place finger on MAX30102 to see real Heart Rate & SpO2.")
        print("  Hold DS18B20 in palm to see real Body Temperature.")
        print("  Press Ctrl+C to stop all services.")
        print("=" * 65)
        print()

        # 5. Start Dashboard
        p_dash = start_service("DASHBOARD", os.path.join(ROOT_DIR, "dashboard", "app.py"))
        processes.append(("Dashboard", p_dash))

        # Monitor
        while True:
            time.sleep(1)
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"[WARNING] Service '{name}' exited with code {proc.returncode}")

    except KeyboardInterrupt:
        print("\n\n[SUPERVISOR] Stopping all services...")
        for name, proc in processes:
            try:
                proc.terminate()
            except Exception:
                pass
        print("[SUPERVISOR] All services stopped.")

if __name__ == "__main__":
    main()
