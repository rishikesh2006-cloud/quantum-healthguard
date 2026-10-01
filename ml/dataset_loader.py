"""
Quantum HealthGuard — Biomedical Dataset Loader & Generator
Creates/loads structured biomedical training datasets (Heart Rate, SpO2, Temperature)
for Classical ML & Qiskit Quantum Machine Learning model training.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import sqlite3
import config

def generate_benchmark_dataset(num_samples: int = 600, random_seed: int = 42):
    """
    Generates a structured biomedical dataset with ground truth health classifications:
    - NORMAL (0)
    - MODERATE (1)
    - HIGH_RISK (2)
    """
    np.random.seed(random_seed)
    n_class = num_samples // 3

    # 1. Normal Vitals (HR: 60-85, SpO2: 96-99%, Temp: 36.3-37.2°C)
    hr_norm   = np.random.normal(72, 5, n_class)
    spo2_norm = np.random.normal(97.8, 0.6, n_class)
    temp_norm = np.random.normal(36.6, 0.2, n_class)
    labels_norm = np.full(n_class, "NORMAL")

    # 2. Moderate Vitals (Elevated HR: 88-110, Slightly low SpO2: 93-95%, Low Fever: 37.4-38.2°C)
    hr_mod   = np.random.normal(98, 8, n_class)
    spo2_mod = np.random.normal(94.2, 0.8, n_class)
    temp_mod = np.random.normal(37.8, 0.3, n_class)
    labels_mod = np.full(n_class, "MODERATE")

    # 3. High Risk / Critical Vitals (Tachycardia: >120, Hypoxia: <92%, High Fever: >38.5°C)
    hr_high   = np.random.uniform(121, 150, n_class)
    spo2_high = np.random.uniform(85, 91.5, n_class)
    temp_high = np.random.uniform(38.6, 40.5, n_class)
    labels_high = np.full(n_class, "HIGH_RISK")

    # Combine into DataFrame
    hr_all   = np.clip(np.concatenate([hr_norm, hr_mod, hr_high]), 40, 160)
    spo2_all = np.clip(np.concatenate([spo2_norm, spo2_mod, spo2_high]), 80, 100)
    temp_all = np.clip(np.concatenate([temp_norm, temp_mod, temp_high]), 34.0, 41.0)
    labels   = np.concatenate([labels_norm, labels_mod, labels_high])

    df = pd.DataFrame({
        "heart_rate": np.round(hr_all, 1),
        "spo2": np.round(spo2_all, 1),
        "temperature": np.round(temp_all, 2),
        "risk_level": labels
    })

    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
    return df


def seed_database_dataset(num_samples: int = 300):
    """Populates healthguard.db SQLite database with initial training telemetry."""
    df = generate_benchmark_dataset(num_samples=num_samples)
    conn = sqlite3.connect(config.DB_PATH)
    
    # Check current row count
    count = conn.execute("SELECT COUNT(*) FROM patient_data").fetchone()[0]
    if count < 50:
        print(f"[DATASET] Seeding database with {len(df)} initial benchmark training samples...")
        for _, row in df.iterrows():
            conn.execute("""
                INSERT INTO patient_data (patient_id, timestamp, heart_rate, spo2, temperature, risk_level)
                VALUES ('P001', datetime('now'), ?, ?, ?, ?)
            """, (row["heart_rate"], row["spo2"], row["temperature"], row["risk_level"]))
        conn.commit()
        print("[DATASET] Database seeding complete!")
    else:
        print(f"[DATASET] Database already contains {count} records. Ready for ML training.")
    conn.close()


if __name__ == "__main__":
    df = generate_benchmark_dataset()
    print("=== Biomedical Dataset Preview ===")
    print(df.head(10))
    print("\nTarget Class Distribution:")
    print(df["risk_level"].value_counts())
    seed_database_dataset()
