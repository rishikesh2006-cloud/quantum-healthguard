"""
Quantum HealthGuard — Master System Entrypoint & Multi-Device Supervisor
Starts all 5 microservices (MQTT Broker, Data Receiver, Sensor Simulator, AI Predictor, Flask Web Server)
concurrently within a single process supervisor and displays local & Wi-Fi LAN access links.

Usage in VS Code / Terminal:
    python main.py
"""

import sys
import os
import time
import subprocess
import socket

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_BIN = sys.executable

def get_lan_ip():
    """Detects local LAN/Wi-Fi IP address for multi-device network connections."""
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
    print("  QUANTUM HEALTHGUARD — MULTI-DEVICE MASTER SUPERVISOR")
    print("  Starting all 5 system microservices...")
    print("=" * 65)
    print()

    processes = []

    try:
        # 1. Start MQTT Broker
        p_broker = start_service("BROKER", os.path.join(ROOT_DIR, "communication", "mqtt_broker.py"))
        processes.append(("Broker", p_broker))
        time.sleep(2)

        # 2. Start MQTT Data Receiver
        p_recv = start_service("RECEIVER", os.path.join(ROOT_DIR, "communication", "mqtt_receiver.py"))
        processes.append(("Receiver", p_recv))
        time.sleep(2)

        # 3. Start Sensor Simulator
        p_sim = start_service("SIMULATOR", os.path.join(ROOT_DIR, "simulator", "sensor_simulator.py"))
        processes.append(("Simulator", p_sim))
        time.sleep(2)

        # 4. Start Real-Time AI Predictor
        p_pred = start_service("PREDICTOR", os.path.join(ROOT_DIR, "ml", "realtime_predict.py"))
        processes.append(("Predictor", p_pred))
        time.sleep(2)

        print()
        print("=" * 65)
        print("  ALL 5 MICROSERVICES OPERATIONAL & MULTI-DEVICE READY!")
        print("  -------------------------------------------------------------")
        print(f"  📱 Mobile / Phone / Tablet URL : http://{lan_ip}:{port}")
        print(f"  💻 Local PC Client View        : http://localhost:{port}")
        print(f"  🛡️ Admin Control Center       : http://localhost:{port}/admin")
        print("  -------------------------------------------------------------")
        print("  Press Ctrl+C to stop all services cleanly.")
        print("=" * 65)
        print()

        # 5. Run Dashboard Server
        p_dash = start_service("DASHBOARD", os.path.join(ROOT_DIR, "dashboard", "app.py"))
        processes.append(("Dashboard", p_dash))

        # Keep supervisor alive & monitor child processes
        while True:
            time.sleep(1)
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"[SUPERVISOR WARNING] Service '{name}' exited with code {proc.returncode}")

    except KeyboardInterrupt:
        print("\n\n[SUPERVISOR] Termination signal received. Stopping all services...")
        for name, proc in processes:
            print(f"[SUPERVISOR] Terminating {name} (PID {proc.pid})...")
            try:
                proc.terminate()
            except Exception:
                pass
        print("[SUPERVISOR] All Quantum HealthGuard services stopped cleanly.")

if __name__ == "__main__":
    main()
