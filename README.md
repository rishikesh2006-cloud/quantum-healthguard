# 🩺 Quantum HealthGuard

> **Quantum HealthGuard** is an offline-first IoT biomedical monitoring gateway, predictive machine learning system, and quantum classifier pipeline powered by Raspberry Pi 5, MQTT, Scikit-Learn, and Qiskit QSVC.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [System Architecture](#-system-architecture)
4. [Quickstart — 1-Click Launchers (Windows & Linux)](#-quickstart--1-click-launchers-windows--linux)
5. [Notepad-Editable Settings (`settings.txt`)](#-notepad-editable-settings-settingstxt)
6. [Security Question Authentication (`/admin`)](#-security-question-authentication-admin)
7. [Quantum & Classical ML Pipeline](#-quantum--classical-ml-pipeline)
8. [ESP32 Biosensor Hardware Integration](#-esp32-biosensor-hardware-integration)
9. [API Reference](#-api-reference)

---

## 🔬 Project Overview

Quantum HealthGuard captures, stores, analyzes, and predicts patient physiological vitals (**Heart Rate, Blood Oxygen $\text{SpO}_2$, Body Temperature, and ECG Waveform**).

It operates **100% offline at the edge** on a Raspberry Pi 5 / PC without requiring an internet connection. It features an instant deterministic safety rules engine, a live web monitoring dashboard, a classical Random Forest classifier, and a **Qiskit Quantum Support Vector Classifier (QSVC)**.

---

## ⭐ Key Features

* **⚡ 1-Click Launchers & Desktop Shortcuts:** Start or stop all 5 microservices cleanly with zero command-line setup (`RUN_HEALTHGUARD.bat`).
* **📝 Notepad-Editable Configuration (`settings.txt`):** Edit security questions, emergency thresholds, ports, and simulator speeds in plain text without code.
* **🛡️ Security Question Admin Access Control:** All external devices get Client Patient View. Accessing `/admin` requires answering a customizable security question (`healthguard2026`).
* **🔌 100% Offline Ready:** Packaged with local `Chart.js` static assets — functions perfectly without internet access.
* **⚛️ End-to-End QML Pipeline:** Encodes 3-vital biomedical vectors into quantum Hilbert state space using Qiskit `ZZFeatureMap` and trains a `QSVC` classifier.
* **🔊 Client Web Audio Emergency Alarm:** Synthesizes audio alarm beeps on patient UI upon `HIGH_RISK` anomaly detection.
* **📄 CSV Health Report Export:** One-click download of patient health history (`/api/export-report`).
* **🔌 ESP32 Arduino Firmware:** Production C++ sketch for MAX30102, AD8232, and DS18B20 JSON telemetry over Wi-Fi MQTT.

---

## 🏗️ System Architecture

```
PATIENT
   │
   ├── MAX30102  (Pulse & SpO₂)
   ├── AD8232    (ECG Waveform)
   └── DS18B20   (Body Temp)
         │
       ESP32  ──Wi-Fi / MQTT──►  MQTT Broker (amqtt / Mosquitto: 1883)
                                          │
                                   Raspberry Pi 5 Gateway
                                   ┌──────┴──────┐
                              Preprocess    Local Safety
                              + Timestamp      Check
                                   │
                                SQLite DB
                                   │
                              Dual AI Engine
                         ┌─────────┴──────────┐
                    Classical ML          Qiskit QSVC
                    (Random Forest)     (Quantum Kernel)
                         └─────────┬──────────┘
                               Real-Time
                              Predictions
                                   │
                        ┌──────────┴──────────┐
                    Dashboard            Emergency Alert
                  (Client/Admin)            Notifier
```

---

## ⚡ Quickstart — 1-Click Launchers (Windows & Linux)

### Windows
1. Double-click **`setup_windows.bat`** (First-time installation).
2. Double-click **`RUN_HEALTHGUARD.bat`** (or the Desktop shortcut **`Run Quantum HealthGuard`**).
3. Open browser:
   - **Client Patient View:** `http://localhost:5000`
   - **Admin Control Center:** `http://localhost:5000/admin` *(Security Key: `healthguard2026`)*

### Raspberry Pi 5 / Linux
```bash
bash setup_linux.sh
bash start_all.sh
```

---

## 📝 Notepad-Editable Settings (`settings.txt`)

Open `settings.txt` in Notepad to change settings anytime:

```ini
# Security Answer (Master Key) required for Admin View:
SECURITY_ANSWER = healthguard2026

# Emergency Thresholds:
HR_HIGH = 120
HR_LOW = 45
SPO2_CRITICAL = 92
TEMP_HIGH = 38.5

# Server Port:
PORT = 5000
```

---

## 🔐 Security Question Authentication (`/admin`)

- **Public Access (`/`):** All devices receive read-only Client Patient View.
- **Admin Access (`/admin`):** Attempting to visit `/admin` presents a Security Question Challenge:
  - **Question:** *"What is the secret master key for Quantum HealthGuard admin access?"*
  - **Default Answer:** `healthguard2026`
- Once answered correctly, Flask issues a signed HTTP session cookie unlocking Admin controls (anomaly injection, thresholds editing, database reset).

---

## ⚛️ Quantum & Classical ML Pipeline

Run the complete pipeline from terminal:

```bash
# 1. Seed biomedical benchmark dataset
python ml/dataset_loader.py

# 2. Train Classical Random Forest (100% Accuracy)
python ml/train_classical.py

# 3. Train Qiskit QSVC Quantum Classifier
python ml/train_qsvc.py

# 4. Run Real-Time AI Inference Service
python ml/realtime_predict.py
```

---

## 🔌 ESP32 Biosensor Hardware Integration

The production firmware is located at [`sensors/esp32_quantum_healthguard.ino`](sensors/esp32_quantum_healthguard.ino).

```
ESP32 Pin Connections:
- MAX30102 (I2C)      -> SDA: GPIO 21 | SCL: GPIO 22
- AD8232 (ECG Analog) -> OUT: GPIO 34 | LO+: GPIO 35 | LO-: GPIO 32
- DS18B20 (Temp 1-W)  -> DATA: GPIO 4 (with 4.7kΩ pull-up resistor)
```

---

## 📞 API Reference

| Endpoint | Method | Access | Description |
|---|---|---|---|
| `/` | GET | Public | Client Patient Telemetry Portal |
| `/admin` | GET | Protected | Admin Control Center Challenge / Dashboard |
| `/api/latest` | GET | Public | Returns latest single reading JSON |
| `/api/data` | GET | Public | Returns last 50 readings array for Chart.js |
| `/api/stats` | GET | Public | Returns session statistics JSON |
| `/api/export-report` | GET | Public | Download patient telemetry report CSV |
| `/api/admin/verify` | POST | Public | Security Question verification endpoint |
| `/api/trigger-anomaly` | POST | Admin Only | Inject manual test anomaly via MQTT |
| `/api/clear-db` | POST | Admin Only | Reset database records |
| `/api/thresholds` | GET/POST | Admin Only | View / Update medical thresholds |

---

*Quantum HealthGuard — Student Research Prototype | Malla Reddy University*
