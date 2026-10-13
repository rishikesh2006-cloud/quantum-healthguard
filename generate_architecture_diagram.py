"""
Generates a high-resolution (300 DPI PNG + Vector SVG) University Presentation
System Architecture Diagram for Quantum HealthGuard.
Style: Clean white background, dark navy-blue headings (#0F2547), solid directional arrows,
and neatly separated hardware and software components across 4 distinct stages.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def create_architecture_diagram(output_png: str, output_svg: str):
    fig, ax = plt.subplots(figsize=(22, 12), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(0, 108)
    ax.set_ylim(0, 58)
    ax.axis("off")

    # Color Palette (University Presentation Style)
    NAVY_DARK    = "#0F2547"
    NAVY_MED     = "#1E3A8A"
    BLUE_ACCENT  = "#0284C7"
    BLUE_LIGHT   = "#F0F7FF"
    TEAL_BORDER  = "#0D9488"
    TEAL_LIGHT   = "#F0FDFA"
    PURPLE_BORD  = "#6D28D9"
    PURPLE_LIGHT = "#F5F3FF"
    AMBER_BORD   = "#D97706"
    AMBER_LIGHT  = "#FFFBEB"
    SLATE_DARK   = "#1E293B"
    SLATE_MUTED  = "#475569"
    GRAY_BOX     = "#F8FAFC"
    GRAY_BORDER  = "#CBD5E1"
    RED_ALERT    = "#DC2626"
    RED_LIGHT    = "#FEF2F2"

    # ─── Top Title Banner ───────────────────────────────────────────────────
    ax.add_patch(FancyBboxPatch(
        (1.5, 52.3), 105.0, 4.5,
        boxstyle="round,pad=0.3,rounding_size=0.6",
        facecolor=NAVY_DARK, edgecolor=NAVY_DARK, linewidth=1.5
    ))
    ax.text(54, 55.15,
            "QUANTUM HEALTHGUARD — SYSTEM ARCHITECTURE & DATA PIPELINE",
            color="#FFFFFF", fontsize=17.5, fontweight="bold", ha="center", va="center",
            fontfamily="DejaVu Sans")
    ax.text(54, 53.25,
            "IoT Healthcare Monitoring with Edge Processing (Raspberry Pi 5) and Quantum Machine Learning (Qiskit QSVC + Random Forest Backup)",
            color="#BAE6FD", fontsize=10.5, fontweight="bold", ha="center", va="center",
            fontfamily="DejaVu Sans")

    # Helper function for Main Stage Containers
    def draw_stage_container(x, y, w, h, stage_num, title, subtitle, hw_tag, border_col, header_bg):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.2,rounding_size=0.7",
            facecolor="#FFFFFF", edgecolor=border_col, linewidth=2.2
        ))
        ax.add_patch(FancyBboxPatch(
            (x, y + h - 4.3), w, 4.3,
            boxstyle="round,pad=0.2,rounding_size=0.7",
            facecolor=header_bg, edgecolor=border_col, linewidth=1.8
        ))
        ax.text(x + w/2, y + h - 1.35, f"STAGE {stage_num}: {title}",
                color="#FFFFFF", fontsize=10.5, fontweight="bold", ha="center", va="center")
        ax.text(x + w/2, y + h - 3.1, subtitle,
                color="#E0F2FE", fontsize=8.8, fontweight="bold", ha="center", va="center")
        ax.add_patch(FancyBboxPatch(
            (x + 0.8, y + h - 6.45), w - 1.6, 1.55,
            boxstyle="round,pad=0.1,rounding_size=0.3",
            facecolor=GRAY_BOX, edgecolor=GRAY_BORDER, linewidth=1.0
        ))
        ax.text(x + w/2, y + h - 5.67, hw_tag,
                color=NAVY_DARK, fontsize=8.1, fontweight="bold", ha="center", va="center")

    # Helper function for inner blocks
    def draw_inner_box(x, y, w, h, title, bullets, bg_color, border_color,
                       title_color=NAVY_DARK, title_size=8.8, text_size=7.8, two_line_title=False):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.15,rounding_size=0.45",
            facecolor=bg_color, edgecolor=border_color, linewidth=1.4
        ))
        title_offset = 1.35 if two_line_title else 1.05
        div_offset   = 2.55 if two_line_title else 1.85
        start_offset = 3.35 if two_line_title else 2.70

        ax.text(x + w/2, y + h - title_offset, title,
                color=title_color, fontsize=title_size, fontweight="bold", ha="center", va="center")
        ax.plot([x + 0.5, x + w - 0.5], [y + h - div_offset, y + h - div_offset],
                color=border_color, linewidth=0.8, alpha=0.6)

        line_y = y + h - start_offset
        avail_h = h - start_offset - 0.4
        line_step = min(avail_h / max(len(bullets), 1), 1.42)
        for b in bullets:
            ax.text(x + 0.6, line_y, b,
                    color=SLATE_DARK, fontsize=text_size, ha="left", va="center")
            line_y -= line_step

    # Helper function for solid directional arrows
    def draw_arrow(x1, y1, x2, y2, label_top="", label_bottom="", color=NAVY_DARK, lw=2.2):
        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle="-|>,head_length=8,head_width=5",
            color=color, linewidth=lw, shrinkA=0, shrinkB=0, zorder=5
        )
        ax.add_patch(arrow)
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        if label_top:
            ax.text(mid_x, mid_y + 1.45, label_top,
                    color=NAVY_DARK, fontsize=8.0, fontweight="bold", ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.25", facecolor="#FFFFFF", edgecolor=color, linewidth=1.1),
                    zorder=6)
        if label_bottom:
            ax.text(mid_x, mid_y - 1.35, label_bottom,
                    color=SLATE_MUTED, fontsize=7.4, fontweight="bold", ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="#F8FAFC", edgecolor="none"),
                    zorder=6)

    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 1: SENSOR DATA COLLECTION — ESP32 (x: 1.5 -> 24.5, width: 23.0)
    # ═══════════════════════════════════════════════════════════════════════════
    draw_stage_container(
        x=1.5, y=9.0, w=23.0, h=41.8,
        stage_num=1,
        title="SENSOR DATA COLLECTION",
        subtitle="Biomedical Sensing & Basic Filtering",
        hw_tag="HARDWARE: Biomedical Sensors + ESP32",
        border_col=BLUE_ACCENT,
        header_bg=NAVY_DARK
    )

    draw_inner_box(
        x=2.3, y=36.2, w=10.2, h=7.1,
        title="1. AD8232 ECG Sensor",
        bullets=[
            "• ECG Electrodes (RA/LA/RL)",
            "• 3.3V & GND -> ESP32",
            "• OUTPUT -> GPIO34 (ADC)",
            "• Lead I Cardiac Waveform"
        ],
        bg_color=BLUE_LIGHT, border_color=BLUE_ACCENT, title_size=8.2, text_size=7.3
    )

    draw_inner_box(
        x=2.3, y=27.6, w=10.2, h=7.3,
        title="2. MAX30102 Sensor",
        bullets=[
            "• Heart Rate (BPM) & SpO2",
            "• VIN -> 3V3 | GND -> GND",
            "• SDA -> GPIO21 (I2C)",
            "• SCL -> GPIO22 (I2C)"
        ],
        bg_color=BLUE_LIGHT, border_color=BLUE_ACCENT, title_size=8.2, text_size=7.3
    )

    draw_inner_box(
        x=2.3, y=19.0, w=10.2, h=7.3,
        title="3. DS18B20 Temp Sensor",
        bullets=[
            "• Body Temperature (°C)",
            "• VCC -> 3V3 | GND -> GND",
            "• DATA -> GPIO4 (1-Wire)",
            "• 4.7 kΩ Pull-up Resistor"
        ],
        bg_color=BLUE_LIGHT, border_color=BLUE_ACCENT, title_size=8.2, text_size=7.3
    )

    draw_inner_box(
        x=13.7, y=19.0, w=10.0, h=24.3,
        title="ESP32 Microcontroller",
        bullets=[
            "[Hardware Acquisition]",
            "• Reads Analog & Digital IO",
            "• Samples 100Hz ECG Trace",
            "",
            "[Software Basic Filtering]",
            "• Removes invalid/NaN data",
            "• Checks sensor lead-off",
            "  & connectivity status",
            "• Moving-average smoothing",
            "• Frames structured JSON",
            "  telemetry packets"
        ],
        bg_color="#F8FAFC", border_color=NAVY_DARK, title_size=8.4, text_size=7.3
    )

    draw_arrow(12.5, 39.7, 13.7, 39.7, color=BLUE_ACCENT, lw=1.8)
    draw_arrow(12.5, 31.2, 13.7, 31.2, color=BLUE_ACCENT, lw=1.8)
    draw_arrow(12.5, 22.6, 13.7, 22.6, color=BLUE_ACCENT, lw=1.8)

    draw_inner_box(
        x=2.3, y=10.0, w=21.4, h=7.5,
        title="ESP32 Structured Telemetry Packet (JSON)",
        bullets=[
            "• Payload: { patient_id, heart_rate, spo2, temperature, ecg_sample }",
            "• Metadata: { sensor_status: 'ONLINE', timestamp }",
            "• Wireless Transmission: 2.4 GHz Wi-Fi MQTT Client"
        ],
        bg_color=GRAY_BOX, border_color=GRAY_BORDER, title_size=8.4, text_size=7.45
    )
    draw_arrow(18.7, 19.0, 18.7, 17.5, color=NAVY_DARK, lw=1.8)

    # ─── Link 1 -> 2: Wi-Fi / MQTT (x: 24.5 -> 30.5, width: 6.0) ────────────
    draw_arrow(24.5, 29.5, 30.5, 29.5,
               label_top="Wi-Fi / MQTT",
               label_bottom="healthguard/vitals",
               color=NAVY_DARK, lw=2.6)

    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 2: EDGE PROCESSING — RASPBERRY PI 5 (x: 30.5 -> 51.5, width: 21.0)
    # ═══════════════════════════════════════════════════════════════════════════
    draw_stage_container(
        x=30.5, y=9.0, w=21.0, h=41.8,
        stage_num=2,
        title="EDGE PROCESSING",
        subtitle="Raspberry Pi 5 Gateway Node",
        hw_tag="HARDWARE: Raspberry Pi 5 | SW: Edge Broker & Filter",
        border_col=TEAL_BORDER,
        header_bg=NAVY_DARK
    )

    draw_inner_box(
        x=31.4, y=36.3, w=19.2, h=7.0,
        title="1. MQTT Broker & Data Validation",
        bullets=[
            "• Receives ESP32 streams over Wi-Fi / MQTT (Port 1883)",
            "• Validates JSON schema, data types & UTC timestamps",
            "• Verifies sensor connectivity & packet integrity"
        ],
        bg_color=TEAL_LIGHT, border_color=TEAL_BORDER, title_size=8.6, text_size=7.55
    )

    draw_inner_box(
        x=31.4, y=28.0, w=19.2, h=7.0,
        title="2. Advanced Noise & Duplicate Filtering",
        bullets=[
            "• Filters noisy spikes, incomplete or corrupted frames",
            "• Eliminates duplicate timestamped sensor readings",
            "• Normalizes physiological streams for downstream AI"
        ],
        bg_color=TEAL_LIGHT, border_color=TEAL_BORDER, title_size=8.6, text_size=7.55
    )

    draw_inner_box(
        x=31.4, y=18.8, w=19.2, h=7.9,
        title="3. Edge Safety Threshold & High-Risk Check",
        bullets=[
            "• Checks vitals against predefined clinical safety limits:",
            "  HR < 45 or > 120 BPM | SpO2 < 92% | Temp > 38.5°C",
            "• Detects immediate high-risk conditions at the edge",
            "• Assigns Edge Safety Status (SAFE / WARNING / HIGH_RISK)"
        ],
        bg_color=AMBER_LIGHT, border_color=AMBER_BORD, title_size=8.6, text_size=7.45
    )

    draw_inner_box(
        x=31.4, y=10.0, w=19.2, h=7.5,
        title="4. Local Edge Buffer & Data Forwarder",
        bullets=[
            "• Temporarily stores validated readings in Edge SQLite DB",
            "• Guarantees zero data loss during network fluctuations",
            "• Forwards processed features & edge status to Laptop"
        ],
        bg_color=GRAY_BOX, border_color=NAVY_DARK, title_size=8.6, text_size=7.55
    )

    draw_arrow(41.0, 36.3, 41.0, 35.0, color=TEAL_BORDER, lw=1.6)
    draw_arrow(41.0, 28.0, 41.0, 26.7, color=TEAL_BORDER, lw=1.6)
    draw_arrow(41.0, 18.8, 41.0, 17.5, color=TEAL_BORDER, lw=1.6)

    # ─── Link 2 -> 3: MQTT / REST API (x: 51.5 -> 57.5, width: 6.0) ─────────
    draw_arrow(51.5, 29.5, 57.5, 29.5,
               label_top="MQTT / REST API",
               label_bottom="Processed Features",
               color=NAVY_DARK, lw=2.6)

    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 3: MAIN ANALYSIS — PROJECT LAPTOP (x: 57.5 -> 82.0, width: 24.5)
    # ═══════════════════════════════════════════════════════════════════════════
    draw_stage_container(
        x=57.5, y=9.0, w=24.5, h=41.8,
        stage_num=3,
        title="MAIN AI & QUANTUM ANALYSIS",
        subtitle="Project Laptop Compute Engine",
        hw_tag="HARDWARE: Project Laptop | SW: Qiskit + Scikit-Learn",
        border_col=PURPLE_BORD,
        header_bg=NAVY_DARK
    )

    draw_inner_box(
        x=58.4, y=37.8, w=22.7, h=5.5,
        title="Processed Feature Vector Extraction",
        bullets=[
            "• Input Vector X = [Heart Rate, SpO2, Temperature] + Edge Status",
            "• StandardScaler Z-score normalization for dual model inference"
        ],
        bg_color=GRAY_BOX, border_color=NAVY_DARK, title_size=8.6, text_size=7.5
    )

    draw_inner_box(
        x=58.4, y=23.2, w=11.0, h=13.0,
        title="PRIMARY ALGORITHM\nQuantum ML (QSVC)",
        bullets=[
            "• Qiskit Quantum Support",
            "  Vector Classifier",
            "• ZZFeatureMap (3 Qubits)",
            "• FidelityQuantumKernel",
            "  Hilbert space mapping",
            "• Classifies health-risk",
            "• Output: QSVC Prediction"
        ],
        bg_color=PURPLE_LIGHT, border_color=PURPLE_BORD, title_color=PURPLE_BORD,
        title_size=8.1, text_size=7.25, two_line_title=True
    )

    draw_inner_box(
        x=70.1, y=23.2, w=11.0, h=13.0,
        title="BACKUP ALGORITHM\nClassical ML (RF)",
        bullets=[
            "• Trained Random Forest",
            "  Classifier (100 Trees)",
            "• Evaluates same scaled",
            "  physiological features",
            "• Standby verification &",
            "  fail-safe classifier",
            "• Output: RF Prediction"
        ],
        bg_color=BLUE_LIGHT, border_color=BLUE_ACCENT, title_color=NAVY_MED,
        title_size=8.1, text_size=7.25, two_line_title=True
    )

    draw_arrow(63.9, 37.8, 63.9, 36.2, color=PURPLE_BORD, lw=1.8)
    draw_arrow(75.6, 37.8, 75.6, 36.2, color=BLUE_ACCENT, lw=1.8)

    draw_inner_box(
        x=58.4, y=10.0, w=22.7, h=11.2,
        title="Risk-Result Comparison & Fallback Decision Stage",
        bullets=[
            "1. Primary Selection: Uses Qiskit QSVC prediction as primary result.",
            "2. Explicit Fallback Logic: Selects Random Forest prediction ONLY",
            "   if QSVC quantum analysis is unavailable, times out, or fails.",
            "3. Safety Comparison: Cross-checks ML result with Pi 5 Edge Safety",
            "   status to produce the Final Health-Risk Classification."
        ],
        bg_color=AMBER_LIGHT, border_color=NAVY_DARK, title_color=NAVY_DARK, title_size=8.5, text_size=7.4
    )

    draw_arrow(63.9, 23.2, 63.9, 21.2, color=PURPLE_BORD, lw=1.8)
    draw_arrow(75.6, 23.2, 75.6, 21.2, color=BLUE_ACCENT, lw=1.8)
    ax.text(61.5, 22.2, "Primary Result", color=PURPLE_BORD, fontsize=7.3, fontweight="bold", ha="center")
    ax.text(78.3, 22.2, "Fallback if QSVC Fails", color=NAVY_MED, fontsize=7.3, fontweight="bold", ha="center")

    # ─── Link 3 -> 4: Final Risk & Decisions (x: 82.0 -> 87.5, width: 5.5) ──
    draw_arrow(82.0, 29.5, 87.5, 29.5,
               label_top="Final Risk",
               label_bottom="& Decisions",
               color=NAVY_DARK, lw=2.6)

    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 4: DASHBOARD AND ALERTS — LAPTOP (x: 87.5 -> 106.5, width: 19.0)
    # ═══════════════════════════════════════════════════════════════════════════
    draw_stage_container(
        x=87.5, y=9.0, w=19.0, h=41.8,
        stage_num=4,
        title="DASHBOARD & ALERTS",
        subtitle="Live Clinical Visualization",
        hw_tag="LAPTOP DISPLAY: Flask Web UI",
        border_col=NAVY_DARK,
        header_bg=NAVY_DARK
    )

    draw_inner_box(
        x=88.3, y=33.5, w=17.4, h=9.8,
        title="Live Physiological Vitals",
        bullets=[
            "• Heart Rate (BPM)",
            "• Blood Oxygen SpO2 (%)",
            "• Body Temperature (°C)",
            "• Live 100Hz ECG Waveform",
            "• Time-Series Trend Graph"
        ],
        bg_color=BLUE_LIGHT, border_color=BLUE_ACCENT, title_size=8.5, text_size=7.55
    )

    draw_inner_box(
        x=88.3, y=21.2, w=17.4, h=11.2,
        title="System & AI Model Outputs",
        bullets=[
            "• Sensor & Comm Status",
            "• Pi 5 Edge Safety Status",
            "• QSVC Prediction (Primary)",
            "• Random Forest (Backup)",
            "• Final Health-Risk Badge",
            "  (NORMAL/MODERATE/HIGH)"
        ],
        bg_color=PURPLE_LIGHT, border_color=PURPLE_BORD, title_size=8.5, text_size=7.55
    )

    draw_inner_box(
        x=88.3, y=10.0, w=17.4, h=10.1,
        title="Emergency Alerts & Logs",
        bullets=[
            "• Real-Time Alert Triggers",
            "• Exact Event Timestamps",
            "• Web Audio Siren Alarm",
            "• CSV Clinical Report Export",
            "• Mobile LAN QR Sync"
        ],
        bg_color=RED_LIGHT, border_color=RED_ALERT, title_color=RED_ALERT, title_size=8.5, text_size=7.55
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # BOTTOM COMPLETE DATA FLOW PIPELINE BAR
    # ═══════════════════════════════════════════════════════════════════════════
    ax.add_patch(FancyBboxPatch(
        (1.5, 1.2), 105.0, 6.0,
        boxstyle="round,pad=0.2,rounding_size=0.5",
        facecolor=GRAY_BOX, edgecolor=NAVY_DARK, linewidth=1.8
    ))
    ax.text(54, 6.0,
            "COMPLETE END-TO-END DATA FLOW PIPELINE",
            color=NAVY_DARK, fontsize=10.0, fontweight="bold", ha="center", va="center")

    flow_nodes = [
        (2.5,  14.5, "Biomedical Sensors\n(AD8232, MAX30102, DS18B20)", BLUE_LIGHT, BLUE_ACCENT),
        (20.0, 16.0, "ESP32 Node\n(Collection + Basic Filtering)", "#FFFFFF", NAVY_DARK),
        (39.0, 18.5, "Raspberry Pi 5 Edge\n(Validation + Safety Check)", TEAL_LIGHT, TEAL_BORDER),
        (60.5, 19.0, "Project Laptop AI\n(Primary QSVC + RF Backup)", PURPLE_LIGHT, PURPLE_BORD),
        (82.5, 11.0, "Final Risk\nClassification", AMBER_LIGHT, AMBER_BORD),
        (96.0,  9.5, "Live Dashboard\n& Alerts", RED_LIGHT, RED_ALERT),
    ]

    for fx, fw, ftext, fbg, fbord in flow_nodes:
        ax.add_patch(FancyBboxPatch(
            (fx, 1.8), fw, 3.1,
            boxstyle="round,pad=0.1,rounding_size=0.35",
            facecolor=fbg, edgecolor=fbord, linewidth=1.3
        ))
        ax.text(fx + fw/2, 3.35, ftext,
                color=NAVY_DARK, fontsize=7.8, fontweight="bold", ha="center", va="center")

    flow_arrows = [
        (17.0, 20.0),
        (36.0, 39.0),
        (57.5, 60.5),
        (79.5, 82.5),
        (93.5, 96.0)
    ]
    for ax1, ax2 in flow_arrows:
        draw_arrow(ax1, 3.35, ax2, 3.35, color=NAVY_DARK, lw=1.8)

    plt.tight_layout(pad=0.3)
    plt.savefig(output_png, dpi=300, facecolor="#FFFFFF")
    plt.savefig(output_svg, format="svg", facecolor="#FFFFFF")
    plt.close(fig)
    print(f"Saved high-res PNG to: {output_png}")
    print(f"Saved vector SVG to  : {output_svg}")

if __name__ == "__main__":
    create_architecture_diagram(
        "c:/Users/Rishikesh/Desktop/Quan/Quantum_HealthGuard_Architecture.png",
        "c:/Users/Rishikesh/Desktop/Quan/Quantum_HealthGuard_Architecture.svg"
    )
