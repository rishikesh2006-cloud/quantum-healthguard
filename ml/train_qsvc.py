"""
Quantum HealthGuard — Qiskit QSVC Quantum Machine Learning Trainer
Trains Quantum Support Vector Classifier (QSVC) using Qiskit ZZFeatureMap encoding
and compares accuracy against Classical Random Forest & SVM.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import pickle
import math
import time

from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.algorithms import QSVC

import config
from ml.dataset_loader import generate_benchmark_dataset

QSVC_MODEL_PATH = config.ROOT_DIR / "ml" / "qsvc_model.pkl"

def train_quantum_classifier(num_samples: int = 150):
    print("=" * 60)
    print("  Quantum HealthGuard — Qiskit QSVC Quantum Classifier Trainer")
    print("=" * 60)

    # 1. Load Data
    df = generate_benchmark_dataset(num_samples=num_samples)
    print(f"\n[QML] Dataset loaded ({len(df)} samples)")
    print(df["risk_level"].value_counts())

    # 2. Encode Labels & Features
    le = LabelEncoder()
    y = le.fit_transform(df["risk_level"])
    X = df[["heart_rate", "spo2", "temperature"]].values

    # Scale features into [0, 2*pi] range suitable for quantum phase encoding
    scaler = MinMaxScaler(feature_range=(0, 2 * math.pi))
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.25, random_state=42, stratify=y
    )

    # 3. Construct Quantum Circuit & Feature Map (3 qubits for HR, SpO2, Temp)
    print("\n[QML] Constructing Qiskit ZZFeatureMap (3 qubits, 2 repetitions)...")
    feature_map = ZZFeatureMap(feature_dimension=3, reps=2, entanglement='linear')

    # 4. Instantiate and Train QSVC
    print("[QML] Training Qiskit Quantum Support Vector Classifier (QSVC)...")
    start_time = time.time()
    qsvc = QSVC(quantum_kernel=None, feature_map=feature_map)
    qsvc.fit(X_train, y_train)
    train_duration = time.time() - start_time
    print(f"[QML] Training finished in {train_duration:.2f} seconds!")

    # 5. Evaluate Predictions
    preds = qsvc.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print("\n" + "=" * 50)
    print(f"  QSVC Quantum Model Test Accuracy: {acc:.2%}")
    print("=" * 50)
    print("\nClassification Metrics Report:")
    print(classification_report(y_test, preds, target_names=le.classes_, zero_division=0))

    # 6. Export Serialized Model & Scaler
    with open(QSVC_MODEL_PATH, "wb") as f:
        pickle.dump({
            "model": qsvc,
            "scaler": scaler,
            "label_encoder": le,
            "accuracy": acc,
            "trained_at": time.time()
        }, f)

    print(f"[QML] Trained Qiskit QSVC model saved to: {QSVC_MODEL_PATH}")
    return acc

if __name__ == "__main__":
    train_quantum_classifier()
