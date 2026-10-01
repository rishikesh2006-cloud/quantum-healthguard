"""
Quantum HealthGuard — Classical ML Trainer
Trains Logistic Regression, Random Forest, SVM on collected data
Run AFTER collecting at least 50+ readings via the simulator
"""

import sqlite3
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

DB_PATH    = os.path.join(os.path.dirname(__file__), "..", "database", "healthguard.db")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "rf_model.pkl")

# ─── Load Data ────────────────────────────────────────────────────────────────
print("[ML] Loading data from database...")
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("""
    SELECT heart_rate, spo2, temperature, risk_level
    FROM patient_data
    WHERE risk_level NOT IN ('UNKNOWN', '')
""", conn)
conn.close()

print(f"[ML] Loaded {len(df)} records.")
print(df["risk_level"].value_counts())

if len(df) < 20:
    print("[ML] ⚠️  Not enough data. Run simulator for at least 5 minutes first.")
    exit()

# ─── Prepare Features ─────────────────────────────────────────────────────────
le      = LabelEncoder()
y       = le.fit_transform(df["risk_level"])
X       = df[["heart_rate", "spo2", "temperature"]].values
scaler  = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
)

# ─── Train Models ─────────────────────────────────────────────────────────────
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest":       RandomForestClassifier(n_estimators=100, random_state=42),
    "SVM (RBF kernel)":    SVC(kernel="rbf", C=1.0, probability=True),
}

results = {}
print("\n" + "=" * 55)
for name, model in models.items():
    model.fit(X_train, y_train)
    preds    = model.predict(X_test)
    acc      = accuracy_score(y_test, preds)
    results[name] = acc
    print(f"\n─── {name} (Acc: {acc:.2%}) ───")
    print(classification_report(y_test, preds, target_names=le.classes_, zero_division=0))

# ─── Summary Table ────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("COMPARISON TABLE")
print(f"{'Model':<25} {'Accuracy':>10}")
print("-" * 36)
for name, acc in sorted(results.items(), key=lambda x: -x[1]):
    print(f"{name:<25} {acc:>10.2%}")

# ─── Save Best Model ──────────────────────────────────────────────────────────
best_name  = max(results, key=results.get)
best_model = models[best_name]

with open(MODEL_PATH, "wb") as f:
    pickle.dump({"model": best_model, "scaler": scaler, "label_encoder": le}, f)

print(f"\n[ML] Best model ({best_name}) saved to {MODEL_PATH}")
