# 🩺 Quantum HealthGuard

> Real-time patient health monitoring using IoT sensors, edge computing on Raspberry Pi,
> classical ML, and Quantum Machine Learning (Qiskit QSVC).

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Architecture](#-architecture)
3. [Quickstart — Windows (Laptop/PC)](#-quickstart--windows-laptoppc)
4. [Quickstart — Raspberry Pi / Linux](#-quickstart--raspberry-pi--linux)
5. [Running the Project](#-running-the-project)
6. [Project Structure](#-project-structure)
7. [Configuration](#-configuration)
8. [Component Descriptions](#-component-descriptions)
9. [Branching Strategy (for teammates)](#-branching-strategy-for-teammates)
10. [Adding Real Hardware](#-adding-real-hardware)
11. [Quantum ML Phase](#-quantum-ml-phase)
12. [Team Contribution Guide](#-team-contribution-guide)

---

## 🔬 Project Overview

Quantum HealthGuard is an IoT + AI health monitoring prototype that:

- Reads **heart rate, SpO₂, ECG, and body temperature** from biomedical sensors
- Transmits data via **ESP32 → MQTT → Raspberry Pi**
- Performs **local edge emergency detection** (works offline)
- Stores data in **SQLite** (locally) and optionally syncs to cloud
- Runs **Classical ML** (Random Forest, SVM, Logistic Regression) for risk classification
- Runs **Quantum ML** (Qiskit QSVC) as a comparison classifier
- Serves a **live web dashboard** accessible from any device on the network

> ⚠️ **Disclaimer:** This is a student research prototype. Not for clinical diagnosis.

---

## 🏗️ Architecture

```
PATIENT
   │
   ├── MAX30102  (HR + SpO₂)
   ├── AD8232    (ECG)
   └── DS18B20   (Temperature)
         │
       ESP32  ──Wi-Fi──►  MQTT Broker (Mosquitto / amqtt)
                                │
                         Raspberry Pi 5
                         ┌──────┴───────┐
                    Preprocess     Local Safety
                    + Timestamp       Check
                         │
                      SQLite DB ──► Cloud (optional)
                         │
                    Feature Extraction
                    ┌────┴──────┐
               Classical ML   Qiskit QSVC
                    └────┬──────┘
                  Risk Classification
                  ┌──────┴──────┐
              Dashboard    Emergency Alert
```

---

## ⚡ Quickstart — Windows (Laptop/PC)

### Prerequisites
- Python 3.10 or higher → https://www.python.org/downloads/ *(check "Add to PATH")*
- Git → https://git-scm.com/download/win

### Steps

```powershell
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/quantum-healthguard.git
cd quantum-healthguard

# 2. Run the one-time setup (double-click or run in terminal)
setup_windows.bat

# 3. Start everything
START_ALL.bat
```

Open your browser at **http://localhost:5000** 🎉

---

## 🐧 Quickstart — Raspberry Pi / Linux

### Prerequisites
- Raspberry Pi OS 64-bit (Bookworm) — or any Debian-based Linux
- Python 3.10+
- Internet connection for first setup

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/quantum-healthguard.git
cd quantum-healthguard

# 2. Run the one-time setup
bash setup_linux.sh

# 3. Start everything
bash start_all.sh
```

Open your browser at **http://\<Pi-IP\>:5000** from any device on the same Wi-Fi.

---

## ▶️ Running the Project

Both platforms use the same components, started in this order:

| Step | Component | Script |
|---|---|---|
| 1 | MQTT Broker | `communication/mqtt_broker.py` (Windows) or Mosquitto (Pi) |
| 2 | Data Receiver | `communication/mqtt_receiver.py` |
| 3 | Sensor Simulator | `simulator/sensor_simulator.py` |
| 4 | Dashboard | `dashboard/app.py` |

**Windows** — `START_ALL.bat` opens 4 terminal windows automatically.  
**Pi/Linux** — `start_all.sh` runs all 4 as background processes.

---

## 📁 Project Structure

```
quantum-healthguard/
│
├── config.py                  ← Central configuration (all settings here)
├── requirements.txt           ← Python dependencies
├── requirements_quantum.txt   ← Qiskit dependencies (install later)
├── .env.example               ← Copy to .env and customize
├── .gitignore
│
├── setup_windows.bat          ← Windows first-time setup
├── setup_linux.sh             ← Pi/Linux first-time setup
├── START_ALL.bat              ← Windows launcher
├── start_all.sh               ← Pi/Linux launcher
│
├── simulator/
│   └── sensor_simulator.py   ← Fake ESP32+sensors (development/testing)
│
├── communication/
│   ├── mqtt_broker.py        ← Pure-Python MQTT broker (Windows, no install)
│   └── mqtt_receiver.py      ← Receives, validates, stores data
│
├── database/                  ← SQLite DB stored here (git-ignored)
│
├── dashboard/
│   ├── app.py                ← Flask web server
│   └── templates/
│       └── index.html        ← Live dashboard UI
│
├── ml/
│   ├── train_classical.py    ← Train RF, LR, SVM
│   └── train_qsvc.py         ← Train Qiskit QSVC (coming in Phase 2)
│
├── sensors/                   ← Real sensor drivers (added when hardware arrives)
│
├── alerts/                    ← Alert logic (SMS, Telegram, etc.)
│
└── logs/                      ← Runtime logs (git-ignored)
```

---

## ⚙️ Configuration

All settings are in [`config.py`](config.py). You can override any value using a `.env` file:

```bash
cp .env.example .env
nano .env    # Edit as needed
```

| Setting | Default | Description |
|---|---|---|
| `MQTT_BROKER` | `localhost` | MQTT broker hostname/IP |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `DASHBOARD_PORT` | `5000` | Flask dashboard port |
| `PATIENT_ID` | `P001` | Default patient identifier |

Emergency thresholds (in `config.py`):

| Vital | Low Alert | High Alert |
|---|---|---|
| Heart Rate | < 45 BPM | > 120 BPM |
| SpO₂ | < 95% (moderate) | < 92% (critical) |
| Temperature | < 35°C | > 38.5°C |

---

## 📦 Component Descriptions

### `simulator/sensor_simulator.py`
Publishes simulated vital signs to MQTT every second. Injects random anomalies 5% of the time to test the alert system. **This is replaced by real sensor code when hardware arrives** — all other components stay the same.

### `communication/mqtt_receiver.py`
Subscribes to MQTT topics, validates incoming data, runs local emergency threshold checks, and writes every reading to the SQLite database. Logs to both console and `logs/receiver.log`.

### `dashboard/app.py`
Flask web server with three API endpoints:
- `GET /` — main dashboard page
- `GET /api/latest` — latest single reading (polled every 3s by JS)
- `GET /api/data` — last 50 readings for charts
- `GET /api/stats` — session statistics

### `ml/train_classical.py`
Trains and compares three classical ML models on data collected from the database. Run after collecting enough readings (50+).

---

## 🌿 Branching Strategy (for teammates)

Each team member works on a **separate branch**:

```bash
# Person A — ML / Quantum
git checkout -b feature/qsvc-classifier

# Person B — Dashboard enhancements
git checkout -b feature/dashboard-charts

# Person C — Real sensor drivers
git checkout -b feature/esp32-sensors

# Person D — Cloud integration
git checkout -b feature/firebase-cloud

# Person E — Alert system
git checkout -b feature/telegram-alerts
```

**To submit your work:**
```bash
git add .
git commit -m "feat: add quantum QSVC classifier"
git push origin feature/qsvc-classifier
# Then open a Pull Request on GitHub
```

---

## 🔌 Adding Real Hardware

When your ESP32 + sensors arrive:

1. Create `sensors/max30102_driver.py` — reads heart rate + SpO₂
2. Create `sensors/ad8232_driver.py` — reads ECG
3. Create `sensors/temperature_driver.py` — reads body temperature
4. Upload `sensors/esp32_main.ino` to ESP32 (publishes JSON to MQTT)
5. **Stop running** `simulator/sensor_simulator.py`
6. Everything else (receiver, dashboard, ML) works unchanged ✅

---

## ⚛️ Quantum ML Phase

After classical ML is working:

```bash
# Install Qiskit (large, takes 5-10 min on Pi)
.venv/bin/pip install -r requirements_quantum.txt

# Train QSVC
python ml/train_qsvc.py
```

Compare results using the output table in `ml/train_classical.py`.

---

## 👥 Team Contribution Guide

| Role | Branch | Files to Work On |
|---|---|---|
| **Hardware / Sensors** | `feature/esp32-sensors` | `sensors/`, ESP32 Arduino code |
| **ML / AI** | `feature/ml-pipeline` | `ml/`, `communication/` |
| **Quantum** | `feature/qsvc` | `ml/train_qsvc.py` |
| **Dashboard / Frontend** | `feature/dashboard` | `dashboard/` |
| **Cloud** | `feature/cloud` | `communication/`, new `cloud/` folder |
| **Alerts** | `feature/alerts` | `alerts/`, `communication/mqtt_receiver.py` |

### Commit Message Convention

```
feat: add new feature
fix:  fix a bug
docs: update documentation
test: add or update tests
refactor: code cleanup without feature change
```

---

## 📞 API Reference

| Endpoint | Method | Returns |
|---|---|---|
| `/` | GET | Dashboard HTML page |
| `/api/latest` | GET | Latest vital signs JSON |
| `/api/data` | GET | Last 50 readings array |
| `/api/stats` | GET | Session statistics JSON |

---

*Quantum HealthGuard — Student Research Prototype*
