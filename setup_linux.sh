#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
#  Quantum HealthGuard — Linux / Raspberry Pi Setup Script
#  Run once after cloning:  bash setup_linux.sh
# ──────────────────────────────────────────────────────────────────────
set -e

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

ok()   { echo -e "${GREEN}[OK]${NC}    $1"; }
skip() { echo -e "${YELLOW}[SKIP]${NC}  $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo "================================================"
echo "   QUANTUM HEALTHGUARD — Linux / Pi Setup"
echo "================================================"
echo

# ── System packages ───────────────────────────────────────────────
echo "[1/5] Updating system packages..."
sudo apt update -q && sudo apt install -y python3-venv python3-pip mosquitto mosquitto-clients -q
ok "System packages updated."

# ── Enable Mosquitto ──────────────────────────────────────────────
echo
echo "[2/5] Enabling Mosquitto MQTT broker..."
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
ok "Mosquitto running."

# ── Virtual Environment ───────────────────────────────────────────
echo
echo "[3/5] Creating Python virtual environment..."
if [ -d ".venv" ]; then
    skip ".venv already exists."
else
    python3 -m venv .venv
    ok "Virtual environment created."
fi

# ── Install Python Packages ───────────────────────────────────────
echo
echo "[4/5] Installing Python dependencies..."
.venv/bin/pip install --upgrade pip --quiet
.venv/bin/pip install -r requirements.txt
ok "All packages installed."

# ── Config & Directories ──────────────────────────────────────────
echo
echo "[5/5] Setting up config and directories..."
[ ! -f ".env" ] && cp .env.example .env && ok "Created .env" || skip ".env exists."
mkdir -p database logs ml sensors
ok "Directories ready."

# ── Make launcher executable ──────────────────────────────────────
chmod +x start_all.sh

echo
echo "================================================"
echo " Setup complete!"
echo " Run:  bash start_all.sh"
echo " Dashboard will be at http://$(hostname -I | awk '{print $1}'):5000"
echo "================================================"
