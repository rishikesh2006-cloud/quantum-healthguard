#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
#  Quantum HealthGuard — Linux / Raspberry Pi Launcher
#  Starts all components in background, shows live logs.
#  Usage:  bash start_all.sh
# ──────────────────────────────────────────────────────────────────────

ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT/.venv/bin/python"
LOG="$ROOT/logs"
mkdir -p "$LOG"

GREEN="\033[0;32m"; NC="\033[0m"
ok() { echo -e "${GREEN}[OK]${NC} $1"; }

echo "=============================================="
echo "  QUANTUM HEALTHGUARD — Starting All Services"
echo "=============================================="
echo

# ── Check Mosquitto ───────────────────────────────────────────────
if systemctl is-active --quiet mosquitto 2>/dev/null; then
    ok "Mosquitto broker already running."
else
    echo "Starting Mosquitto..."
    sudo systemctl start mosquitto
    sleep 1
    ok "Mosquitto started."
fi

# ── MQTT Receiver ─────────────────────────────────────────────────
echo "Starting MQTT Receiver..."
nohup "$VENV" "$ROOT/communication/mqtt_receiver.py" \
    > "$LOG/receiver.log" 2>&1 &
RECV_PID=$!
ok "Receiver started (PID $RECV_PID)"
sleep 1

# ── Sensor Simulator ──────────────────────────────────────────────
echo "Starting Sensor Simulator..."
nohup "$VENV" "$ROOT/simulator/sensor_simulator.py" \
    > "$LOG/simulator.log" 2>&1 &
SIM_PID=$!
ok "Simulator started (PID $SIM_PID)"
sleep 1

# ── Dashboard ─────────────────────────────────────────────────────
echo "Starting Dashboard..."
nohup "$VENV" "$ROOT/dashboard/app.py" \
    > "$LOG/dashboard.log" 2>&1 &
DASH_PID=$!
ok "Dashboard started (PID $DASH_PID)"
sleep 2

echo
IP=$(hostname -I | awk '{print $1}')
echo "=============================================="
echo "  ALL SERVICES RUNNING"
echo "  Dashboard → http://$IP:5000"
echo "  Logs      → $LOG/"
echo "  Stop all  → kill $RECV_PID $SIM_PID $DASH_PID"
echo "=============================================="
