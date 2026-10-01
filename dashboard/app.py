"""
Quantum HealthGuard — Flask Dashboard
Live vitals, historical charts, risk status.
Access at: http://localhost:5000  (or http://<Pi-IP>:5000 from any device on the network)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify
import sqlite3
from dotenv import load_dotenv

load_dotenv()
import config

app = Flask(__name__)


def get_readings(limit: int = 50) -> list[dict]:
    if not config.DB_PATH.exists():
        return []
    conn  = sqlite3.connect(config.DB_PATH)
    rows  = conn.execute("""
        SELECT timestamp, heart_rate, spo2, temperature, risk_level
        FROM patient_data
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [
        {"timestamp": r[0], "heart_rate": r[1], "spo2": r[2],
         "temperature": r[3], "risk": r[4]}
        for r in reversed(rows)
    ]


@app.route("/")
def index():
    readings = get_readings(1)
    latest   = readings[0] if readings else {}
    return render_template("index.html", latest=latest)


@app.route("/api/data")
def api_data():
    """Last 50 readings as JSON — used by Chart.js on the dashboard."""
    return jsonify(get_readings(50))


@app.route("/api/latest")
def api_latest():
    """Single latest reading — polled every 3 seconds by the dashboard."""
    readings = get_readings(1)
    return jsonify(readings[0] if readings else {})


@app.route("/api/stats")
def api_stats():
    """Summary statistics for the monitoring session."""
    if not config.DB_PATH.exists():
        return jsonify({})
    conn   = sqlite3.connect(config.DB_PATH)
    row    = conn.execute("""
        SELECT COUNT(*), AVG(heart_rate), MIN(heart_rate), MAX(heart_rate),
               AVG(spo2), AVG(temperature),
               SUM(CASE WHEN risk_level='HIGH_RISK' THEN 1 ELSE 0 END)
        FROM patient_data
    """).fetchone()
    conn.close()
    return jsonify({
        "total_readings": row[0],
        "avg_hr": round(row[1] or 0, 1),
        "min_hr": round(row[2] or 0, 1),
        "max_hr": round(row[3] or 0, 1),
        "avg_spo2": round(row[4] or 0, 1),
        "avg_temp": round(row[5] or 0, 2),
        "high_risk_count": row[6] or 0,
    })


if __name__ == "__main__":
    print(f"[DASH] Dashboard → http://localhost:{config.DASHBOARD_PORT}")
    app.run(
        host=config.DASHBOARD_HOST,
        port=config.DASHBOARD_PORT,
        debug=config.DASHBOARD_DEBUG,
    )
