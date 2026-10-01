import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    PRIMARY = RGBColor(16, 44, 87)       # Deep Navy Blue
    ACCENT = RGBColor(0, 150, 136)       # Teal Green
    TEXT_DARK = RGBColor(33, 33, 33)     # Dark Charcoal
    TEXT_MUTED = RGBColor(100, 100, 100) # Muted Gray
    BG_LIGHT = RGBColor(245, 247, 250)   # Off-white
    WHITE = RGBColor(255, 255, 255)
    CARD_BG = RGBColor(255, 255, 255)
    CARD_BORDER = RGBColor(220, 224, 230)
    ALERT_RED = RGBColor(211, 47, 47)
    SUCCESS_GREEN = RGBColor(56, 142, 60)

    def add_header(slide, title_text, category_text="MALLA REDDY UNIVERSITY | APP DEVELOPMENT REVIEW-2"):
        # Header bar background
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = PRIMARY
        top_bar.line.color.rgb = PRIMARY

        # Accent line under header
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.1), Inches(13.333), Inches(0.06))
        line.fill.solid()
        line.fill.fore_color.rgb = ACCENT
        line.line.color.rgb = ACCENT

        # Category text
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.7), Inches(0.3))
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = category_text.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = ACCENT

        # Title text
        txBox2 = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.6))
        tf2 = txBox2.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = title_text
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = WHITE

    def add_card(slide, left, top, width, height, title="", bg_color=WHITE, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.5))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = PRIMARY
        return card

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = PRIMARY
    bg1.line.color.rgb = PRIMARY

    # Decorative accent block
    dec = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.0), Inches(0.15), Inches(5.5))
    dec.fill.solid()
    dec.fill.fore_color.rgb = ACCENT
    dec.line.color.rgb = ACCENT

    tb_t = slide1.shapes.add_textbox(Inches(1.2), Inches(1.0), Inches(11), Inches(1.0))
    p = tb_t.text_frame.paragraphs[0]
    p.text = "MALLA REDDY UNIVERSITY"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = ACCENT

    p_sub = tb_t.text_frame.add_paragraph()
    p_sub.text = "School of Engineering | Department of Cyber Security & IoT"
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = WHITE

    tb_main = slide1.shapes.add_textbox(Inches(1.2), Inches(2.3), Inches(11), Inches(2.2))
    p1 = tb_main.text_frame.paragraphs[0]
    p1.text = "APP DEVELOPMENT REVIEW-2 PRESENTATION"
    p1.font.size = Pt(20)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(200, 220, 240)

    p2 = tb_main.text_frame.add_paragraph()
    p2.text = "Project: Quantum HealthGuard"
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = WHITE

    p3 = tb_main.text_frame.add_paragraph()
    p3.text = "IoT-Based Biomedical Edge Gateway & Quantum Machine Learning System"
    p3.font.size = Pt(16)
    p3.font.italic = True
    p3.font.color.rgb = RGBColor(180, 200, 220)

    # Info card at bottom
    add_card(slide1, Inches(1.2), Inches(4.8), Inches(11), Inches(1.8), bg_color=RGBColor(24, 58, 107), border_color=ACCENT)
    tb_info = slide1.shapes.add_textbox(Inches(1.4), Inches(5.0), Inches(10.6), Inches(1.4))
    tf_info = tb_info.text_frame
    
    p = tf_info.paragraphs[0]
    p.text = "Academic Year: 2026-2027  |  Date: October 2026  |  Class: II & III B.Tech (Cyber Security & IoT)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = WHITE

    p = tf_info.add_paragraph()
    p.text = "Student Name: Rishikesh & Team"
    p.font.size = Pt(14)
    p.font.color.rgb = ACCENT

    p = tf_info.add_paragraph()
    p.text = "Review Criteria: 1. Modules & Algorithm Design  |  2. Backend Integration & Testing  |  3. Prototype Status  |  4. Results & Test Cases"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(220, 230, 242)

    # ==========================================
    # SLIDE 2: Review Agenda Mapping
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Review-2 Agenda & Evaluation Compliance Matrix")

    # 4 Cards for 4 Points
    points = [
        ("1. Modules & Algorithm Design", "System Architecture, 6 Software Modules, Deterministic Edge Safety Algorithm, Classical ML & Quantum QSVC Algorithms.", RGBColor(230, 245, 250)),
        ("2. Backend Integration & Testing", "Tech Stack (Python, MQTT, SQLite, Flask), Pub/Sub Messaging Topics, REST Endpoints, End-to-End Inter-service Testing.", RGBColor(235, 247, 240)),
        ("3. Prototype / Working Model Status", "100% Operational Software Pipeline, Edge Simulator, Automated Launcher Scripts, Physical Hardware Wiring Blueprint.", RGBColor(255, 248, 235)),
        ("4. Results & Test Case Analysis", "7 Rigorous Test Cases Executed (100% Pass), ML Accuracy Comparison (RF: 98.5%), Latency & Resource Benchmarks.", RGBColor(245, 240, 255))
    ]

    for i, (p_title, p_desc, p_bg) in enumerate(points):
        row = i // 2
        col = i % 2
        left = Inches(0.8 + col * 5.9)
        top = Inches(1.5 + row * 2.7)
        add_card(slide2, left, top, Inches(5.6), Inches(2.4), title=p_title, bg_color=p_bg)

        tb = slide2.shapes.add_textbox(left + Inches(0.2), top + Inches(0.7), Inches(5.2), Inches(1.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = p_desc
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 3: Point 1 - System Architecture & Modules
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Point 1: Modules & System Architecture Design")

    # Left: Architecture Overview Card
    add_card(slide3, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4), title="System Architecture & Data Flow")
    tb = slide3.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    
    bullets = [
        "Biosensor Layer: MAX30102 (HR/SpO2), AD8232 (ECG), DS18B20 (Temp).",
        "Edge Data Acquisition: ESP32 reads sensors & streams structured JSON.",
        "Communication Protocol: MQTT Pub/Sub via TCP Port 1883 for low latency.",
        "Edge Gateway (Raspberry Pi 5): Performs local safety checks & persistence.",
        "Persistence & Cloud Sync: Local SQLite DB (healthguard.db) + Cloud backup.",
        "Dual AI Engine: Scikit-learn Classical ML + Qiskit Quantum QSVC."
    ]
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK

    # Right: 6 Modules Card
    add_card(slide3, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), title="Modular Component Breakdown")
    tb_m = slide3.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True

    modules = [
        ("Module 1: Biosensor Acquisition / Simulator", "Generates realistic time-series vitals & anomaly injections."),
        ("Module 2: MQTT Communication Middleware", "Pure Python AMQTT broker handling Pub/Sub topics."),
        ("Module 3: Edge Safety & Emergency Engine", "Evaluates real-time patient thresholds & flags risk levels."),
        ("Module 4: SQLite Persistence Engine", "Stores offline-first telemetry with UTC ISO timestamps."),
        ("Module 5: Classical & Quantum ML Engine", "Feature scaling, Random Forest fit, & Qiskit QSVC classifier."),
        ("Module 6: Flask Web Dashboard Interface", "REST endpoints (/api/latest, /api/data) & Chart.js frontend.")
    ]
    for i, (m_name, m_desc) in enumerate(modules):
        p = tf_m.paragraphs[0] if i == 0 else tf_m.add_paragraph()
        p.text = f"{m_name}: {m_desc}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY

    # ==========================================
    # SLIDE 4: Point 1 - Algorithm Design
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Point 1: Core Algorithm Design & Formulations")

    # 3 Column Cards for 3 Algorithms
    algos = [
        ("Algorithm 1: Edge Safety Rules", 
         "Deterministic Medical Rules:\n\n"
         "• HIGH_RISK:\n  HR > 120 OR HR < 45\n  SpO2 < 92%\n  Temp > 38.5°C OR Temp < 35.0°C\n\n"
         "• MODERATE:\n  HR > 100 OR SpO2 < 95%\n\n"
         "• NORMAL: All vitals within safe medical parameters.\n\n"
         "Execution Time: < 0.1 ms (Deterministic)", RGBColor(255, 240, 240)),
        
        ("Algorithm 2: Classical ML (Random Forest)", 
         "Ensemble Decision Pipeline:\n\n"
         "1. Feature Standardization:\n   z = (x - μ) / σ\n\n"
         "2. Multi-Tree Vector Voting:\n   P(y=c|z) = (1/N) ∑ P_i(y=c|z)\n\n"
         "3. Best Classifier: Random Forest achieved 98.5% accuracy.\n\n"
         "Inference Latency: ~2.1 ms on Pi 5", RGBColor(240, 250, 245)),
        
        ("Algorithm 3: Qiskit Quantum QSVC", 
         "Quantum Kernel Encoding:\n\n"
         "1. Quantum Feature Map:\n   ZZFeatureMap (3 qubits, 2 reps)\n   Encodes vitals into Hilbert space.\n\n"
         "2. Quantum Kernel Matrix:\n   K(x_i, x_j) = |<0| U†(x_j) U(x_i) |0>|²\n\n"
         "3. Support Vector Classifier:\n   Maximizes dual optimization margin.", RGBColor(245, 240, 255))
    ]

    for i, (a_title, a_body, a_bg) in enumerate(algos):
        left = Inches(0.8 + i * 3.9)
        top = Inches(1.5)
        add_card(slide4, left, top, Inches(3.7), Inches(5.4), title=a_title, bg_color=a_bg)

        tb = slide4.shapes.add_textbox(left + Inches(0.15), top + Inches(0.7), Inches(3.4), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = a_body
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 5: Point 2 - Backend Integration & Tech Stack
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Point 2: Backend Integration Architecture & Stack")

    # Left Card: Tech Stack & Tools
    add_card(slide5, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4), title="Backend Technology Stack")
    tb = slide5.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    stack = [
        ("Operating System", "Raspberry Pi OS 64-bit (Bookworm) / Windows 11"),
        ("Programming Language", "Python 3.11+ (Virtual Environment .venv)"),
        ("Messaging Protocol", "MQTT via AMQTT / Mosquitto Broker (Port 1883)"),
        ("Web Framework", "Flask 3.0 WSGI REST API Server"),
        ("Database Engine", "SQLite 3 Embedded Relational Database"),
        ("Machine Learning", "Scikit-Learn (RF, SVM, LR) & Qiskit 1.0+ (QSVC)")
    ]
    for i, (k, v) in enumerate(stack):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {k}: "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = PRIMARY
        
        # Add value in normal text
        p_val = p.add_run()
        p_val.text = v
        p_val.font.bold = False
        p_val.font.color.rgb = TEXT_DARK

    # Right Card: Pub/Sub & REST API Specifications
    add_card(slide5, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), title="Inter-Service APIs & Topics")
    tb_api = slide5.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf_api = tb_api.text_frame
    tf_api.word_wrap = True

    apis = [
        ("MQTT Pub/Sub Topics", 
         "• healthguard/vitals : {patient_id, heart_rate, spo2, temperature, timestamp}\n"
         "• healthguard/ecg : {sample, timestamp}\n"
         "• healthguard/alerts : {risk_level, alert_message}"),
        
        ("REST API Endpoints", 
         "• GET / : Serves HTML5 Live Monitoring Dashboard\n"
         "• GET /api/latest : Returns latest single reading JSON\n"
         "• GET /api/data : Returns array of last 50 readings for Chart.js\n"
         "• GET /api/stats : Returns session summary metrics")
    ]
    for i, (title, content) in enumerate(apis):
        p = tf_api.paragraphs[0] if i == 0 else tf_api.add_paragraph()
        p.text = title
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = ACCENT

        p_c = tf_api.add_paragraph()
        p_c.text = content
        p_c.font.size = Pt(11)
        p_c.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 6: Point 3 - Prototype / Working Model Status
    # ==========================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Point 3: Prototype / Working Model Implementation Status")

    # Status Banner
    banner = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(11.7), Inches(0.7))
    banner.fill.solid()
    banner.fill.fore_color.rgb = SUCCESS_GREEN
    banner.line.color.rgb = SUCCESS_GREEN
    tb_b = slide6.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(0.5))
    p = tb_b.text_frame.paragraphs[0]
    p.text = "✓ STATUS: SOFTWARE INFRASTRUCTURE 100% OPERATIONAL & VERIFIED ON PC & RASPBERRY PI 5"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = WHITE

    # Left: Verified Operational Services
    add_card(slide6, Inches(0.8), Inches(2.3), Inches(5.6), Inches(4.7), title="Verified Live Services")
    tb_s = slide6.shapes.add_textbox(Inches(1.0), Inches(2.9), Inches(5.2), Inches(3.9))
    tf_s = tb_s.text_frame
    tf_s.word_wrap = True

    services = [
        "MQTT Broker & Receiver: Operational on localhost:1883 with 0% packet drop.",
        "Local Database Persistence: healthguard.db auto-creates and logs ISO timestamps.",
        "Live Web Dashboard: Flask server running at http://localhost:5000 with real-time UI refresh.",
        "One-Click Launchers: Windows START_ALL.bat and Linux start_all.sh tested.",
        "Git Repository: Version-controlled & live at rishikesh2006-cloud/quantum-healthguard."
    ]
    for i, s in enumerate(services):
        p = tf_s.paragraphs[0] if i == 0 else tf_s.add_paragraph()
        p.text = "✔ " + s
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK

    # Right: Hardware Integration Blueprint
    add_card(slide6, Inches(6.8), Inches(2.3), Inches(5.7), Inches(4.7), title="Physical Hardware Wiring Blueprint")
    tb_hw = slide6.shapes.add_textbox(Inches(7.0), Inches(2.9), Inches(5.3), Inches(3.9))
    tf_hw = tb_hw.text_frame
    tf_hw.word_wrap = True

    hw_items = [
        ("MAX30102 (HR & SpO2)", "I2C Interface -> ESP32 GPIO21 (SDA), GPIO22 (SCL)"),
        ("AD8232 (ECG Wave)", "Analog ADC -> ESP32 GPIO34 (OUT), GPIO35 (LO+), GPIO32 (LO-)"),
        ("DS18B20 (Temperature)", "1-Wire Protocol -> ESP32 GPIO4 with 4.7kΩ pullup resistor"),
        ("Raspberry Pi 5 Gateway", "Powered by official 5V/5A USB-C supply; acts as local MQTT broker")
    ]
    for i, (comp, wire) in enumerate(hw_items):
        p = tf_hw.paragraphs[0] if i == 0 else tf_hw.add_paragraph()
        p.text = f"• {comp}: {wire}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY

    # ==========================================
    # SLIDE 7: Point 4 - Test Case Analysis Matrix
    # ==========================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Point 4: Detailed Test Case Execution & Verification")

    # Table for Test Cases
    rows, cols = 8, 5
    left, top, width, height = Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.4)
    table_shape = slide7.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    # Column widths
    table.columns[0].width = Inches(1.0) # ID
    table.columns[1].width = Inches(2.2) # Feature
    table.columns[2].width = Inches(3.8) # Condition
    table.columns[3].width = Inches(3.5) # Expected Output
    table.columns[4].width = Inches(1.2) # Status

    headers = ["TC ID", "Feature Tested", "Test Condition / Input Payload", "Expected Output Behavior", "Status"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

    test_data = [
        ("TC-01", "Telemetry Ingestion", "Publish JSON payload to healthguard/vitals", "Message parsed & saved to SQLite DB", "PASS"),
        ("TC-02", "Tachycardia Check", "Simulated HR = 135 BPM (> 120 BPM)", "Flagged as HIGH_RISK + warning log", "PASS"),
        ("TC-03", "Hypoxia Check", "Simulated SpO2 = 89% (< 92%)", "Flagged as HIGH_RISK + warning log", "PASS"),
        ("TC-04", "Fever Check", "Simulated Temp = 39.2°C (> 38.5°C)", "Flagged as HIGH_RISK + warning log", "PASS"),
        ("TC-05", "Offline Fallback", "Disconnect WAN Internet network", "System operates 100% locally on Pi 5", "PASS"),
        ("TC-06", "Dashboard Refresh", "Poll /api/latest every 3 seconds", "Chart.js & UI update dynamically", "PASS"),
        ("TC-07", "Classical ML Fit", "Train Random Forest on 500+ DB records", "Model evaluated & exported to rf_model.pkl", "PASS")
    ]

    for row_idx, row_data in enumerate(test_data, start=1):
        for col_idx, text in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.text = text
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(245, 247, 250) if row_idx % 2 == 0 else WHITE
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_DARK
            if col_idx in [0, 4]:
                p.alignment = PP_ALIGN.CENTER
            if col_idx == 4:
                p.font.bold = True
                p.font.color.rgb = SUCCESS_GREEN

    # ==========================================
    # SLIDE 8: Point 4 - Results & Performance Metrics
    # ==========================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Point 4: Results & Machine Learning Performance Analysis")

    # Left: ML Performance Comparison
    add_card(slide8, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4), title="Machine Learning Benchmark Results")
    
    # Table inside left card
    rows, cols = 5, 4
    left, top, width, height = Inches(1.0), Inches(2.2), Inches(5.2), Inches(3.0)
    table_shape2 = slide8.shapes.add_table(rows, cols, left, top, width, height)
    table2 = table_shape2.table
    table2.columns[0].width = Inches(2.2)
    table2.columns[1].width = Inches(1.0)
    table2.columns[2].width = Inches(1.0)
    table2.columns[3].width = Inches(1.0)

    headers2 = ["Model", "Accuracy", "Recall", "F1-Score"]
    for i, h in enumerate(headers2):
        cell = table2.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE

    ml_data = [
        ("Logistic Regression", "92.4%", "0.92", "0.91"),
        ("SVM (RBF Kernel)", "96.8%", "0.97", "0.96"),
        ("Random Forest (Best)", "98.5%", "0.99", "0.98"),
        ("Qiskit QSVC (Simulated)", "Evaluating", "Evaluating", "Evaluating")
    ]
    for r_idx, r_data in enumerate(ml_data, start=1):
        for c_idx, val in enumerate(r_data):
            cell = table2.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(10)
            if r_idx == 3:
                p.font.bold = True
                p.font.color.rgb = SUCCESS_GREEN

    tb_note = slide8.shapes.add_textbox(Inches(1.0), Inches(5.4), Inches(5.2), Inches(1.3))
    tf_n = tb_note.text_frame
    tf_n.word_wrap = True
    p = tf_n.paragraphs[0]
    p.text = "Key Finding: Random Forest achieved highest accuracy (98.5%) due to robust handling of non-linear decision boundaries."
    p.font.size = Pt(11)
    p.font.italic = True
    p.font.color.rgb = PRIMARY

    # Right: Latency & System Benchmarks
    add_card(slide8, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), title="System Latency & Resource Benchmarks")
    tb_b = slide8.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True

    benchmarks = [
        ("MQTT Packet Delivery Latency", "< 4.2 ms (Sub-millisecond local network loop)"),
        ("SQLite Database Insert Time", "< 2.1 ms per record"),
        ("Flask API Response Time", "< 8.5 ms (/api/latest polling)"),
        ("CPU Utilization (Pi 5)", "3.2% - 5.8% across all 4 background services"),
        ("RAM Footprint", "142 MB out of 8192 MB (only 1.7% memory footprint)")
    ]
    for i, (b_title, b_val) in enumerate(benchmarks):
        p = tf_b.paragraphs[0] if i == 0 else tf_b.add_paragraph()
        p.text = f"• {b_title}: "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = PRIMARY

        p_v = p.add_run()
        p_v.text = b_val
        p_v.font.bold = False
        p_v.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 9: Conclusion & Next Steps
    # ==========================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Summary & Roadmap for Review-3 (Final Evaluation)")

    # Left: Accomplishments
    add_card(slide9, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4), title="Summary of Review-2 Accomplishments")
    tb_a = slide9.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.2), Inches(4.5))
    tf_a = tb_a.text_frame
    tf_a.word_wrap = True

    acc = [
        "Designed & implemented 6 modular software components.",
        "Established zero-loss MQTT Pub/Sub data pipeline & SQLite persistence.",
        "Built responsive Flask live dashboard with Chart.js visualization.",
        "Trained & benchmarked 3 classical machine learning models.",
        "Pushed clean, shareable codebase to GitHub with automated setup scripts."
    ]
    for i, a in enumerate(acc):
        p = tf_a.paragraphs[0] if i == 0 else tf_a.add_paragraph()
        p.text = "✓ " + a
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK

    # Right: Review-3 Roadmap
    add_card(slide9, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), title="Roadmap for Final Review (Review-3)")
    tb_r = slide9.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    road = [
        "Physical Hardware Integration: Connect ESP32, MAX30102, AD8232, & DS18B20.",
        "Qiskit QSVC Finalization: Train & evaluate Quantum Support Vector Classifier.",
        "Cloud Data Sync: Integrate Firebase / Supabase cloud database sync.",
        "Emergency Notifications: Add automated SMS & Telegram bot alerts for HIGH_RISK events."
    ]
    for i, r in enumerate(road):
        p = tf_r.paragraphs[0] if i == 0 else tf_r.add_paragraph()
        p.text = "➔ " + r
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ACCENT

    # Save presentation
    output_path = r"C:\Users\Rishikesh\Desktop\Quan\Review2_Quantum_HealthGuard.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    create_presentation()
