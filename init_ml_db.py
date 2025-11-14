"""Initialize ML detection database schema."""

import sqlite3

def init_ml_db():
    conn = sqlite3.connect('detections_ml.db')
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
    print("ML detection database initialized: detections_ml.db")

if __name__ == "__main__":
    init_ml_db()
