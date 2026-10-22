"""
Quantum HealthGuard — Professional System Architecture Diagram Generator (v2)
Generates a high-resolution (300 DPI PNG + Vector SVG) university presentation
diagram with clean white background, dark navy-blue headings, solid directional
arrows, and neatly separated hardware and software components.

Usage:
    python generate_architecture_diagram.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import textwrap

# ═════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═════════════════════════════════════════════════════════════════════════════

# Color palette — university / IEEE presentation style
NAVY      = "#0B1D3A"
NAVY_HDR  = "#0F2547"
NAVY_MED  = "#1B3A6B"
BLUE      = "#0369A1"
BLUE_LT   = "#EFF6FF"
TEAL      = "#0F766E"
TEAL_LT   = "#F0FDFA"
PURPLE    = "#6D28D9"
PURPLE_LT = "#F5F3FF"
AMBER     = "#B45309"
AMBER_LT  = "#FFFBEB"
RED       = "#DC2626"
RED_LT    = "#FEF2F2"
GREEN     = "#15803D"
SLATE     = "#334155"
SLATE_LT  = "#64748B"
GRAY      = "#F1F5F9"
GRAY_BD   = "#CBD5E1"
WHITE     = "#FFFFFF"
BLACK     = "#0F172A"

# Layout dimensions
FIG_W, FIG_H = 24, 14
COORD_W, COORD_H = 120, 70

# Stage X-positions and widths
S1_X, S1_W = 1.5, 26
S2_X, S2_W = 31, 22
S3_X, S3_W = 56.5, 27
S4_X, S4_W = 87, 19.5
STAGE_Y, STAGE_H = 9, 46

# Gaps between stages for arrows
GAP_12_X1, GAP_12_X2 = S1_X + S1_W, S2_X
GAP_23_X1, GAP_23_X2 = S2_X + S2_W, S3_X
GAP_34_X1, GAP_34_X2 = S3_X + S3_W, S4_X


def draw_rounded_box(ax, x, y, w, h, fc=WHITE, ec=GRAY_BD, lw=1.4, radius=0.6):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.15,rounding_size={radius}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2
    ))


def draw_header_bar(ax, x, y, w, h, text, sub="", fc=NAVY_HDR, ec=NAVY_HDR):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.15,rounding_size=0.6",
        facecolor=fc, edgecolor=ec, linewidth=1.6, zorder=3
    ))
    ax.text(x + w / 2, y + h * 0.65, text,
            color=WHITE, fontsize=10.5, fontweight="bold",
            ha="center", va="center", zorder=4)
    if sub:
        ax.text(x + w / 2, y + h * 0.22, sub,
                color="#93C5FD", fontsize=8.5, fontweight="bold",
                ha="center", va="center", zorder=4)


def draw_label_bar(ax, x, y, w, h, text, fc=GRAY, ec=GRAY_BD):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.1,rounding_size=0.35",
        facecolor=fc, edgecolor=ec, linewidth=0.9, zorder=3
    ))
    ax.text(x + w / 2, y + h / 2, text,
            color=NAVY, fontsize=7.8, fontweight="bold",
            ha="center", va="center", zorder=4)


def draw_inner_card(ax, x, y, w, h, title, bullets, fc=WHITE, ec=GRAY_BD,
                    tc=NAVY, ts=8.6, bs=7.4, multi_title=False):
    draw_rounded_box(ax, x, y, w, h, fc=fc, ec=ec, lw=1.3, radius=0.45)

    # Title
    title_y_off = 1.5 if multi_title else 1.1
    ax.text(x + w / 2, y + h - title_y_off, title,
            color=tc, fontsize=ts, fontweight="bold",
            ha="center", va="center", zorder=4)

    # Divider
    div_y = y + h - (2.4 if multi_title else 1.85)
    ax.plot([x + 0.5, x + w - 0.5], [div_y, div_y],
            color=ec, linewidth=0.7, alpha=0.5, zorder=3)

    # Bullets
    start_y = div_y - 0.85
    avail = start_y - y - 0.3
    step = min(avail / max(len(bullets), 1), 1.38)
    for i, b in enumerate(bullets):
        ax.text(x + 0.6, start_y - i * step, b,
                color=BLACK, fontsize=bs, ha="left", va="center", zorder=4)


def draw_arrow(ax, x1, y1, x2, y2, label="", sublabel="",
               color=NAVY, lw=2.4, head_l=8, head_w=5):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=f"-|>,head_length={head_l},head_width={head_w}",
        color=color, linewidth=lw, shrinkA=0, shrinkB=0, zorder=5
    )
    ax.add_patch(arr)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    if label:
        ax.text(mx, my + 1.5, label, color=NAVY, fontsize=8, fontweight="bold",
                ha="center", va="center", zorder=6,
                bbox=dict(boxstyle="round,pad=0.25", fc=WHITE, ec=color, lw=1.0))
    if sublabel:
        ax.text(mx, my - 1.2, sublabel, color=SLATE_LT, fontsize=7.2,
                fontweight="bold", ha="center", va="center", zorder=6)


def draw_small_arrow(ax, x1, y1, x2, y2, color=NAVY, lw=1.5):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>,head_length=6,head_width=4",
        color=color, linewidth=lw, shrinkA=0, shrinkB=0, zorder=5
    )
    ax.add_patch(arr)


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN DIAGRAM BUILDER
# ═════════════════════════════════════════════════════════════════════════════

def create_diagram(out_png: str, out_svg: str):
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=300)
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, COORD_W)
    ax.set_ylim(0, COORD_H)
    ax.axis("off")

    # ─── Title Banner ───────────────────────────────────────────────────
    ax.add_patch(FancyBboxPatch(
        (1, 63), COORD_W - 2, 5.8,
        boxstyle="round,pad=0.3,rounding_size=0.6",
        facecolor=NAVY, edgecolor=NAVY, linewidth=1.5, zorder=3
    ))
    ax.text(COORD_W / 2, 67.3,
            "QUANTUM HEALTHGUARD — SYSTEM ARCHITECTURE & DATA PIPELINE",
            color=WHITE, fontsize=18, fontweight="bold",
            ha="center", va="center", zorder=4)
    ax.text(COORD_W / 2, 65,
            "IoT Healthcare Monitoring  |  Edge Processing (Raspberry Pi 5)  |  "
            "Quantum Machine Learning (Qiskit QSVC + Random Forest Backup)",
            color="#93C5FD", fontsize=10.5, fontweight="bold",
            ha="center", va="center", zorder=4)

    # ═════════════════════════════════════════════════════════════════════
    #  STAGE 1 — SENSOR DATA COLLECTION (ESP32)
    # ═════════════════════════════════════════════════════════════════════
    draw_rounded_box(ax, S1_X, STAGE_Y, S1_W, STAGE_H, ec=BLUE, lw=2.2)
    draw_header_bar(ax, S1_X, STAGE_Y + STAGE_H - 4.5, S1_W, 4.5,
                    "STAGE 1: SENSOR DATA COLLECTION",
                    "ESP32 Microcontroller Node")
    draw_label_bar(ax, S1_X + 0.8, STAGE_Y + STAGE_H - 6.6, S1_W - 1.6, 1.6,
                   "HARDWARE: 3 Biomedical Sensors + ESP32 DevKit")

    # Three sensor cards (left column)
    sensor_x = S1_X + 0.8
    sensor_w = 11.5

    draw_inner_card(ax, sensor_x, 38.8, sensor_w, 7.0,
                    "1. AD8232 ECG Sensor",
                    ["• ECG Electrodes (RA/LA/RL)",
                     "• 3.3V & GND → ESP32",
                     "• OUTPUT → GPIO34 (ADC)",
                     "• Lead-I Cardiac Waveform"],
                    fc=BLUE_LT, ec=BLUE, ts=8.2, bs=7.2)

    draw_inner_card(ax, sensor_x, 30.6, sensor_w, 7.0,
                    "2. MAX30102 HR & SpO₂",
                    ["• Heart Rate (BPM) & SpO₂ (%)",
                     "• VIN → 3V3 | GND → GND",
                     "• SDA → GPIO21 (I²C)",
                     "• SCL → GPIO22 (I²C)"],
                    fc=BLUE_LT, ec=BLUE, ts=8.2, bs=7.2)

    draw_inner_card(ax, sensor_x, 22.2, sensor_w, 7.2,
                    "3. DS18B20 Temperature",
                    ["• Body Temperature (°C)",
                     "• VCC → 3V3 | GND → GND",
                     "• DATA → GPIO4 (1-Wire)",
                     "• 4.7 kΩ Pull-up Resistor"],
                    fc=BLUE_LT, ec=BLUE, ts=8.2, bs=7.2)

    # ESP32 MCU card (right column)
    esp_x = S1_X + 13.5
    esp_w = 12.0

    draw_inner_card(ax, esp_x, 22.2, esp_w, 23.6,
                    "ESP32 Microcontroller",
                    ["[Hardware Acquisition]",
                     "• Reads Analog & Digital I/O",
                     "• 100 Hz ECG ADC Sampling",
                     "",
                     "[Basic Filtering (Software)]",
                     "• Removes invalid / NaN data",
                     "• AD8232 lead-off detection",
                     "• MAX30102 finger presence",
                     "  threshold (IR > 50000)",
                     "• DS18B20 fault code filter",
                     "• 4-point moving avg filter",
                     "• Frames structured JSON",
                     "  telemetry packets"],
                    fc=GRAY, ec=NAVY_HDR, ts=8.4, bs=7.1)

    # Sensor → ESP32 arrows
    for sy in [42.3, 34.1, 25.8]:
        draw_small_arrow(ax, sensor_x + sensor_w, sy, esp_x, sy, color=BLUE, lw=1.6)

    # ESP32 output packet box
    draw_inner_card(ax, S1_X + 0.8, 10.0, S1_W - 1.6, 10.5,
                    "ESP32 Structured Telemetry Packet (JSON)",
                    ["• patient_id, heart_rate, spo2, temperature",
                     "• ecg_sample (raw ADC value)",
                     "• sensor_status: 'ONLINE (AD8232+MAX30102+DS18B20)'",
                     "• timestamp (Unix epoch seconds)",
                     "• Wi-Fi 2.4 GHz MQTT Client Publisher"],
                    fc=GRAY, ec=GRAY_BD, ts=8.3, bs=7.3)
    draw_small_arrow(ax, esp_x + esp_w / 2, 22.2, esp_x + esp_w / 2, 20.5,
                     color=NAVY, lw=1.6)

    # ─── Arrow: Stage 1 → Stage 2 ──────────────────────────────────────
    draw_arrow(ax, GAP_12_X1, 32, GAP_12_X2, 32,
               label="Wi-Fi / MQTT", sublabel="healthguard/vitals",
               color=NAVY, lw=2.6)

    # ═════════════════════════════════════════════════════════════════════
    #  STAGE 2 — EDGE PROCESSING (RASPBERRY PI 5)
    # ═════════════════════════════════════════════════════════════════════
    draw_rounded_box(ax, S2_X, STAGE_Y, S2_W, STAGE_H, ec=TEAL, lw=2.2)
    draw_header_bar(ax, S2_X, STAGE_Y + STAGE_H - 4.5, S2_W, 4.5,
                    "STAGE 2: EDGE PROCESSING",
                    "Raspberry Pi 5 Gateway Node")
    draw_label_bar(ax, S2_X + 0.8, STAGE_Y + STAGE_H - 6.6, S2_W - 1.6, 1.6,
                   "HW: Raspberry Pi 5 | SW: Edge Broker & Filter")

    inner_x2 = S2_X + 0.8
    inner_w2 = S2_W - 1.6

    draw_inner_card(ax, inner_x2, 38.6, inner_w2, 6.8,
                    "1. MQTT Broker & Data Validation",
                    ["• Receives ESP32 packets via Wi-Fi / MQTT (Port 1883)",
                     "• Validates JSON schema, data types & UTC timestamps",
                     "• Verifies sensor connectivity & packet integrity"],
                    fc=TEAL_LT, ec=TEAL, ts=8.4, bs=7.4)

    draw_inner_card(ax, inner_x2, 30.8, inner_w2, 6.6,
                    "2. Noise, Incomplete & Duplicate Filtering",
                    ["• Filters noisy spikes & incomplete readings",
                     "• Eliminates duplicate timestamped packets",
                     "• Normalizes streams for downstream AI"],
                    fc=TEAL_LT, ec=TEAL, ts=8.4, bs=7.4)

    draw_inner_card(ax, inner_x2, 22.0, inner_w2, 7.6,
                    "3. Edge Safety Threshold Check",
                    ["• Checks vitals against predefined safety limits:",
                     "  HR < 45 or > 120 BPM | SpO₂ < 92% | Temp > 38.5°C",
                     "• Detects immediate high-risk conditions at edge",
                     "• Assigns Edge Safety Status (SAFE / WARNING / HIGH_RISK)"],
                    fc=AMBER_LT, ec=AMBER, ts=8.4, bs=7.3)

    draw_inner_card(ax, inner_x2, 10.0, inner_w2, 10.5,
                    "4. Local Edge Buffer & Forwarder",
                    ["• Stores validated readings in Edge SQLite DB",
                     "• Guarantees zero data loss during network outages",
                     "• Forwards processed features & edge safety status",
                     "  to Project Laptop via MQTT (healthguard/processed)",
                     "• Exposes REST API (/api/latest) for Dashboard polling"],
                    fc=GRAY, ec=NAVY_HDR, ts=8.4, bs=7.3)

    # Stage 2 internal vertical arrows
    for top, bot in [(38.6, 37.4), (30.8, 29.6), (22.0, 20.5)]:
        draw_small_arrow(ax, S2_X + S2_W / 2, top, S2_X + S2_W / 2, bot,
                         color=TEAL, lw=1.4)

    # ─── Arrow: Stage 2 → Stage 3 ──────────────────────────────────────
    draw_arrow(ax, GAP_23_X1, 32, GAP_23_X2, 32,
               label="MQTT / REST API", sublabel="healthguard/processed",
               color=NAVY, lw=2.6)

    # ═════════════════════════════════════════════════════════════════════
    #  STAGE 3 — MAIN ANALYSIS (PROJECT LAPTOP)
    # ═════════════════════════════════════════════════════════════════════
    draw_rounded_box(ax, S3_X, STAGE_Y, S3_W, STAGE_H, ec=PURPLE, lw=2.2)
    draw_header_bar(ax, S3_X, STAGE_Y + STAGE_H - 4.5, S3_W, 4.5,
                    "STAGE 3: MAIN AI & QUANTUM ANALYSIS",
                    "Project Laptop Compute Engine")
    draw_label_bar(ax, S3_X + 0.8, STAGE_Y + STAGE_H - 6.6, S3_W - 1.6, 1.6,
                   "HW: Project Laptop | SW: Qiskit + Scikit-Learn + Flask")

    inner_x3 = S3_X + 0.8
    inner_w3 = S3_W - 1.6

    # Feature Extraction bar
    draw_inner_card(ax, inner_x3, 40.0, inner_w3, 5.2,
                    "Processed Feature Vector Extraction",
                    ["• Input Vector X = [Heart Rate, SpO₂, Temperature] + Edge Status",
                     "• StandardScaler Z-score normalization for dual model inference"],
                    fc=GRAY, ec=NAVY_HDR, ts=8.6, bs=7.5)

    # Dual algorithm cards side by side
    alg_w = inner_w3 / 2 - 0.4
    left_x  = inner_x3
    right_x = inner_x3 + inner_w3 / 2 + 0.4

    draw_inner_card(ax, left_x, 25.0, alg_w, 13.2,
                    "PRIMARY ALGORITHM\nQuantum ML (QSVC)",
                    ["• Qiskit Quantum Support",
                     "  Vector Classifier",
                     "• ZZFeatureMap (3 Qubits)",
                     "• FidelityQuantumKernel",
                     "  → Hilbert-space mapping",
                     "• Classifies health-risk",
                     "  patterns from vitals",
                     "• Output: QSVC Prediction"],
                    fc=PURPLE_LT, ec=PURPLE, tc=PURPLE,
                    ts=8.0, bs=7.1, multi_title=True)

    draw_inner_card(ax, right_x, 25.0, alg_w, 13.2,
                    "BACKUP ALGORITHM\nClassical ML (RF)",
                    ["• Trained Random Forest",
                     "  Classifier (100 Trees)",
                     "• Evaluates same scaled",
                     "  physiological features",
                     "• Standby fail-safe",
                     "  classifier",
                     "• Activated ONLY if QSVC fails",
                     "• Output: RF Prediction"],
                    fc=BLUE_LT, ec=BLUE, tc=NAVY_MED,
                    ts=8.0, bs=7.1, multi_title=True)

    # Arrows from Feature Extraction → algorithms
    draw_small_arrow(ax, left_x + alg_w / 2, 40.0, left_x + alg_w / 2, 38.2,
                     color=PURPLE, lw=1.6)
    draw_small_arrow(ax, right_x + alg_w / 2, 40.0, right_x + alg_w / 2, 38.2,
                     color=BLUE, lw=1.6)

    # Risk-Result Comparison & Fallback Decision
    draw_inner_card(ax, inner_x3, 10.0, inner_w3, 13.0,
                    "Risk-Result Comparison & Fallback Decision Engine",
                    ["1. Primary Selection: Uses Qiskit QSVC prediction as",
                     "   the primary classification result.",
                     "",
                     "2. Explicit Fallback Logic: Selects Random Forest ONLY",
                     "   if QSVC is unavailable, times out, or raises an error.",
                     "",
                     "3. Edge Safety Override: Cross-checks ML result with",
                     "   Raspberry Pi 5 Edge Safety status — immediate",
                     "   physiological threshold breaches are never masked."],
                    fc=AMBER_LT, ec=NAVY_HDR, tc=NAVY,
                    ts=8.5, bs=7.2)

    # Arrows from algorithms → Decision Engine
    draw_small_arrow(ax, left_x + alg_w / 2, 25.0, left_x + alg_w / 2, 23.0,
                     color=PURPLE, lw=1.6)
    draw_small_arrow(ax, right_x + alg_w / 2, 25.0, right_x + alg_w / 2, 23.0,
                     color=BLUE, lw=1.6)

    # Labels on decision arrows
    ax.text(left_x + alg_w / 2, 24.0, "Primary Result",
            color=PURPLE, fontsize=7.0, fontweight="bold",
            ha="center", va="center", zorder=6)
    ax.text(right_x + alg_w / 2, 24.0, "Fallback if QSVC Fails",
            color=NAVY_MED, fontsize=7.0, fontweight="bold",
            ha="center", va="center", zorder=6)

    # ─── Arrow: Stage 3 → Stage 4 ──────────────────────────────────────
    draw_arrow(ax, GAP_34_X1, 32, GAP_34_X2, 32,
               label="Final Risk", sublabel="& Decisions",
               color=NAVY, lw=2.6)

    # ═════════════════════════════════════════════════════════════════════
    #  STAGE 4 — DASHBOARD & ALERTS (LAPTOP DISPLAY)
    # ═════════════════════════════════════════════════════════════════════
    draw_rounded_box(ax, S4_X, STAGE_Y, S4_W, STAGE_H, ec=NAVY_HDR, lw=2.2)
    draw_header_bar(ax, S4_X, STAGE_Y + STAGE_H - 4.5, S4_W, 4.5,
                    "STAGE 4: DASHBOARD & ALERTS",
                    "Live Clinical Visualization")
    draw_label_bar(ax, S4_X + 0.8, STAGE_Y + STAGE_H - 6.6, S4_W - 1.6, 1.6,
                   "LAPTOP DISPLAY: Flask Web UI (Port 5000)")

    inner_x4 = S4_X + 0.8
    inner_w4 = S4_W - 1.6

    draw_inner_card(ax, inner_x4, 35.6, inner_w4, 9.6,
                    "Live Physiological Vitals",
                    ["• Heart Rate (BPM)",
                     "• Blood Oxygen SpO₂ (%)",
                     "• Body Temperature (°C)",
                     "• Live 100 Hz ECG Waveform",
                     "• Time-Series Trend Graph"],
                    fc=BLUE_LT, ec=BLUE, ts=8.4, bs=7.5)

    draw_inner_card(ax, inner_x4, 23.0, inner_w4, 11.4,
                    "System & AI Model Outputs",
                    ["• Sensor & Communication Status",
                     "• Pi 5 Edge Safety Status",
                     "• QSVC Prediction (Primary)",
                     "• Random Forest Prediction (Backup)",
                     "• Final Health-Risk Classification",
                     "  (NORMAL / MODERATE / HIGH_RISK)"],
                    fc=PURPLE_LT, ec=PURPLE, ts=8.4, bs=7.5)

    draw_inner_card(ax, inner_x4, 10.0, inner_w4, 11.8,
                    "Emergency Alerts & Logs",
                    ["• Real-Time Audio/Visual Alerts",
                     "• Exact Event Timestamps",
                     "• Web Audio Siren Alarm",
                     "• CSV Clinical Report Export",
                     "• Mobile LAN Wi-Fi QR Sync",
                     "• Admin Control Center Access"],
                    fc=RED_LT, ec=RED, tc=RED, ts=8.4, bs=7.5)

    # ═════════════════════════════════════════════════════════════════════
    #  BOTTOM — COMPLETE END-TO-END DATA FLOW BAR
    # ═════════════════════════════════════════════════════════════════════
    bar_y = 1
    bar_h = 6.2
    draw_rounded_box(ax, 1, bar_y, COORD_W - 2, bar_h, fc=GRAY, ec=NAVY, lw=1.6)
    ax.text(COORD_W / 2, bar_y + bar_h - 1.2,
            "COMPLETE END-TO-END DATA FLOW PIPELINE",
            color=NAVY, fontsize=10, fontweight="bold",
            ha="center", va="center", zorder=4)

    # Flow nodes
    flow_nodes = [
        (2.5,  16.5, "Biomedical Sensors\n(AD8232, MAX30102, DS18B20)",   BLUE_LT,   BLUE),
        (21.5, 17.0, "ESP32 Node\n(Collection + Basic Filtering)",       WHITE,     NAVY),
        (41.0, 19.5, "Raspberry Pi 5 Edge\n(Validation + Safety Check)",  TEAL_LT,  TEAL),
        (63.0, 20.0, "Project Laptop AI\n(Primary QSVC + RF Backup)",    PURPLE_LT, PURPLE),
        (85.5, 12.0, "Final Risk\nClassification",                        AMBER_LT, AMBER),
        (100.0, 10.0, "Live Dashboard\n& Alerts",                         RED_LT,   RED),
    ]

    for nx, nw, ntxt, nfc, nec in flow_nodes:
        draw_rounded_box(ax, nx, bar_y + 0.6, nw, 3.2,
                         fc=nfc, ec=nec, lw=1.2, radius=0.35)
        ax.text(nx + nw / 2, bar_y + 2.2, ntxt,
                color=NAVY, fontsize=7.6, fontweight="bold",
                ha="center", va="center", zorder=4)

    # Flow arrows
    flow_pairs = [(19.0, 21.5), (38.5, 41.0), (60.5, 63.0), (83.0, 85.5), (97.5, 100.0)]
    for x1, x2 in flow_pairs:
        draw_small_arrow(ax, x1, bar_y + 2.2, x2, bar_y + 2.2, color=NAVY, lw=1.6)

    # ─── Save ───────────────────────────────────────────────────────────
    plt.tight_layout(pad=0.3)
    plt.savefig(out_png, dpi=300, facecolor=WHITE, bbox_inches="tight")
    plt.savefig(out_svg, format="svg", facecolor=WHITE, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved high-res PNG : {out_png}")
    print(f"[OK] Saved vector SVG  : {out_svg}")


if __name__ == "__main__":
    create_diagram(
        "c:/Users/Rishikesh/Desktop/Quan/Quantum_HealthGuard_Architecture.png",
        "c:/Users/Rishikesh/Desktop/Quan/Quantum_HealthGuard_Architecture.svg"
    )
