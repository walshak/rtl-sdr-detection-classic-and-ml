"""Initialize ML detection database schema."""

import sqlite3
import os

def init_ml_db():
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    db_path = os.path.join(data_dir, 'detections_ml.db')
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS detections_ml (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            freq REAL,
            label TEXT,
            peak_power REAL,
            noise_floor REAL,
            snr REAL,
            bandwidth REAL,
            kurtosis REAL,
            skewness REAL,
            num_peaks INTEGER,
            power_spectrum BLOB,
            device_label TEXT,
            device_lat REAL,
            device_long REAL,
            raw_samples BLOB,
            iso_forest_anomaly BOOLEAN,
            cnn_predicted_label TEXT,
            cnn_confidence REAL
        )
    ''')
    conn.commit()
    conn.close()
    return db_path

if __name__ == "__main__":
    db_path = init_ml_db()
    print(f"ML detection database initialized: {db_path}")
