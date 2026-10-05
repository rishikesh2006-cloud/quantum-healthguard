"""
Quantum HealthGuard — Flask Web Application Server
Serves both Client (Patient/Caregiver) and Admin Control Center interfaces.
Optimized for multi-device access (Mobiles, Tablets, Laptops) across Wi-Fi/LAN networks.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, Response
import sqlite3
import json
import time
import csv
import io
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY


# ─── Helper Functions ──────────────────────────────────────────────────────────

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


def is_admin_authenticated() -> bool:
    return session.get("is_admin") is True


def publish_mqtt_msg(topic, payload):
    try:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        except AttributeError:
            client = mqtt.Client()
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 10)
        client.publish(topic, json.dumps(payload))
        client.disconnect()
        return True
    except Exception as e:
        print(f"[ADMIN MQTT ERROR] {e}")
        return False


def get_db_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_readings(limit: int = 50, patient_id: str = None) -> list[dict]:
    if not config.DB_PATH.exists():
        return []
    conn = get_db_connection()
    if patient_id:
        rows = conn.execute("""
            SELECT id, timestamp, patient_id, heart_rate, spo2, temperature, risk_level
            FROM patient_data
            WHERE patient_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (patient_id, limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT id, timestamp, patient_id, heart_rate, spo2, temperature, risk_level
            FROM patient_data
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


# ─── CLIENT / PATIENT ROUTES ──────────────────────────────────────────────────

@app.route("/")
def client_dashboard():
    """Client / Patient & Caregiver Monitoring View — Mobile & Multi-Device Optimized"""
    readings = get_readings(1)
    latest = readings[0] if readings else {}
    lan_ip = get_lan_ip()
    lan_url = f"http://{lan_ip}:{config.DASHBOARD_PORT}"
    return render_template("index.html", latest=latest, is_admin=is_admin_authenticated(), lan_url=lan_url, lan_ip=lan_ip)


# ─── ADMIN ROUTES & SECURITY QUESTION AUTH ───────────────────────────────────

@app.route("/admin")
def admin_dashboard():
    """
    Admin Management & Control Center View.
    Protected: Only accessible if authenticated via Security Question challenge.
    """
    if not is_admin_authenticated():
        return render_template("admin_auth.html", question=config.ADMIN_SECURITY_QUESTION)
    lan_ip = get_lan_ip()
    return render_template("admin.html", lan_ip=lan_ip)


@app.route("/api/admin/verify", methods=["POST"])
def api_admin_verify():
    """Verifies the Security Question Answer and grants Admin session access."""
    data = request.json or {}
    user_answer = data.get("answer", "").strip()

    if user_answer.lower() == config.ADMIN_SECURITY_ANSWER.lower():
        session["is_admin"] = True
        return jsonify({"status": "success", "message": "Admin access granted"})
    else:
        return jsonify({"status": "error", "message": "Incorrect security answer"}), 401


@app.route("/api/admin/logout", methods=["POST"])
def api_admin_logout():
    """Logs out from Admin session."""
    session.pop("is_admin", None)
    return jsonify({"status": "success", "message": "Admin logged out"})


# ─── REST API ENDPOINTS ────────────────────────────────────────────────────────

@app.route("/api/info")
def api_info():
    """Returns system device network URLs for mobile discovery."""
    lan_ip = get_lan_ip()
    return jsonify({
        "device": "Quantum HealthGuard Gateway",
        "local_url": f"http://localhost:{config.DASHBOARD_PORT}",
        "mobile_lan_url": f"http://{lan_ip}:{config.DASHBOARD_PORT}",
        "lan_ip": lan_ip,
        "port": config.DASHBOARD_PORT
    })


@app.route("/api/latest")
def api_latest():
    patient_id = request.args.get("patient_id")
    readings = get_readings(1, patient_id=patient_id)
    return jsonify(readings[0] if readings else {})


@app.route("/api/data")
def api_data():
    limit = int(request.args.get("limit", 50))
    patient_id = request.args.get("patient_id")
    return jsonify(get_readings(limit, patient_id=patient_id))


@app.route("/api/stats")
def api_stats():
    if not config.DB_PATH.exists():
        return jsonify({
            "total_readings": 0, "avg_hr": 0, "min_hr": 0, "max_hr": 0,
            "avg_spo2": 0, "avg_temp": 0, "high_risk_count": 0, "db_size_kb": 0
        })
    conn = get_db_connection()
    row = conn.execute("""
        SELECT COUNT(*), AVG(heart_rate), MIN(heart_rate), MAX(heart_rate),
               AVG(spo2), AVG(temperature),
               SUM(CASE WHEN risk_level='HIGH_RISK' THEN 1 ELSE 0 END),
               SUM(CASE WHEN risk_level='MODERATE' THEN 1 ELSE 0 END),
               SUM(CASE WHEN risk_level='NORMAL' THEN 1 ELSE 0 END)
        FROM patient_data
    """).fetchone()
    conn.close()

    db_size = os.path.getsize(config.DB_PATH) // 1024 if config.DB_PATH.exists() else 0

    return jsonify({
        "total_readings": row[0] or 0,
        "avg_hr": round(row[1] or 0, 1),
        "min_hr": round(row[2] or 0, 1),
        "max_hr": round(row[3] or 0, 1),
        "avg_spo2": round(row[4] or 0, 1),
        "avg_temp": round(row[5] or 0, 2),
        "high_risk_count": row[6] or 0,
        "moderate_count": row[7] or 0,
        "normal_count": row[8] or 0,
        "db_size_kb": db_size
    })


@app.route("/api/export-report")
def api_export_report():
    """Generates downloadable CSV patient health report for Client or Admin."""
    if not config.DB_PATH.exists():
        return Response("No data available", status=404)

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, timestamp, patient_id, heart_rate, spo2, temperature, risk_level
        FROM patient_data ORDER BY id DESC LIMIT 500
    """).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Record ID", "UTC Timestamp", "Patient ID", "Heart Rate (BPM)", "SpO2 (%)", "Temperature (C)", "Risk Classification"])

    for r in rows:
        writer.writerow([r["id"], r["timestamp"], r["patient_id"], r["heart_rate"], r["spo2"], r["temperature"], r["risk_level"]])

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=Quantum_HealthGuard_Report.csv"
    return response


# ─── PROTECTED ADMIN API ENDPOINTS ──────────────────────────────────────────────

@app.route("/api/records")
def api_records():
    """Paginated database records viewer for Admin"""
    if not is_admin_authenticated():
        return jsonify({"error": "Admin authentication required"}), 403

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    offset = (page - 1) * per_page
    risk_filter = request.args.get("risk", "")

    conn = get_db_connection()
    if risk_filter:
        total = conn.execute("SELECT COUNT(*) FROM patient_data WHERE risk_level=?", (risk_filter,)).fetchone()[0]
        rows = conn.execute("""
            SELECT id, timestamp, patient_id, heart_rate, spo2, temperature, risk_level
            FROM patient_data WHERE risk_level=?
            ORDER BY id DESC LIMIT ? OFFSET ?
        """, (risk_filter, per_page, offset)).fetchall()
    else:
        total = conn.execute("SELECT COUNT(*) FROM patient_data").fetchone()[0]
        rows = conn.execute("""
            SELECT id, timestamp, patient_id, heart_rate, spo2, temperature, risk_level
            FROM patient_data
            ORDER BY id DESC LIMIT ? OFFSET ?
        """, (per_page, offset)).fetchall()
    conn.close()

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if total > 0 else 1,
        "records": [dict(r) for r in rows]
    })


@app.route("/api/trigger-anomaly", methods=["POST"])
def api_trigger_anomaly():
    """Admin Trigger: Injects instant abnormal test reading via MQTT"""
    if not is_admin_authenticated():
        return jsonify({"error": "Admin authentication required"}), 403

    data = request.json or {}
    anomaly_type = data.get("type", "tachycardia")
    patient_id = data.get("patient_id", config.DEFAULT_PATIENT_ID)

    vitals = {
        "patient_id": patient_id,
        "heart_rate": 75.0,
        "spo2": 98.0,
        "temperature": 36.6,
        "timestamp": time.time()
    }

    if anomaly_type == "tachycardia":
        vitals["heart_rate"] = 138.5
    elif anomaly_type == "hypoxia":
        vitals["spo2"] = 88.5
    elif anomaly_type == "fever":
        vitals["temperature"] = 39.4
    elif anomaly_type == "critical_combined":
        vitals["heart_rate"] = 142.0
        vitals["spo2"] = 87.0
        vitals["temperature"] = 39.8

    success = publish_mqtt_msg(config.MQTT_TOPICS["vitals"], vitals)
    if success:
        return jsonify({"status": "success", "message": f"Injected '{anomaly_type}' anomaly via MQTT", "payload": vitals})
    else:
        return jsonify({"status": "error", "message": "Failed to publish to MQTT Broker"}), 500


@app.route("/api/clear-db", methods=["POST"])
def api_clear_db():
    """Admin action: Reset database records"""
    if not is_admin_authenticated():
        return jsonify({"error": "Admin authentication required"}), 403

    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM patient_data")
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Database cleared successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/thresholds", methods=["GET", "POST"])
def api_thresholds():
    """View / Update System Safety Thresholds"""
    if request.method == "POST":
        if not is_admin_authenticated():
            return jsonify({"error": "Admin authentication required"}), 403

        new_thr = request.json or {}
        if "hr_high" in new_thr: config.THRESHOLDS["heart_rate"]["high"] = float(new_thr["hr_high"])
        if "hr_low" in new_thr:  config.THRESHOLDS["heart_rate"]["low"] = float(new_thr["hr_low"])
        if "spo2_critical" in new_thr: config.THRESHOLDS["spo2"]["critical"] = float(new_thr["spo2_critical"])
        if "temp_high" in new_thr: config.THRESHOLDS["temperature"]["high"] = float(new_thr["temp_high"])
        return jsonify({"status": "success", "thresholds": config.THRESHOLDS})

    return jsonify({"thresholds": config.THRESHOLDS})


if __name__ == "__main__":
    lan_ip = get_lan_ip()
    print("=" * 60)
    print("  QUANTUM HEALTHGUARD — MULTI-DEVICE WEB SERVER")
    print(f"  Local PC Access  : http://localhost:{config.DASHBOARD_PORT}")
    print(f"  Mobile/Wi-Fi URL : http://{lan_ip}:{config.DASHBOARD_PORT}")
    print("=" * 60)
    app.run(host=config.DASHBOARD_HOST, port=config.DASHBOARD_PORT, debug=False)
