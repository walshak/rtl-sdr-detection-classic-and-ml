import sqlite3
import os

def init_db():
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    db_path = os.path.join(data_dir, 'detections.db')
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            freq REAL,
            label TEXT,
            bandwidth REAL,
            peak_power REAL,
            noise_floor REAL,
            snr REAL,
            mean_power REAL,
            std_power REAL,
            min_power REAL,
            max_power REAL,
            kurtosis REAL,
            skewness REAL,
            num_peaks INTEGER,
            power_spectrum BLOB,
            device_label TEXT,
            device_lat REAL,
            device_long REAL,
            raw_samples BLOB,
            fft_history BLOB,
            -- New fields for comprehensive analysis
            confidence_score REAL,
            signal_duration REAL,
            center_freq_offset REAL,
            bandwidth_efficiency REAL,
            spectral_centroid REAL,
            spectral_rolloff REAL,
            spectral_flux REAL,
            zero_crossing_rate REAL,
            peak_frequencies BLOB,
            modulation_index REAL,
            phase_variance REAL,
            amplitude_variance REAL,
            dominant_frequency REAL,
            frequency_stability REAL,
            scan_number INTEGER,
            detection_sequence INTEGER,
            baseline_deviation REAL,
            signal_quality_index REAL,
            interference_level REAL,
            doppler_shift REAL,
            activity_score REAL
        )
    ''')
    conn.commit()
    conn.close()
    return db_path

if __name__ == "__main__":
    db_path = init_db()
    print(f"Database initialized: {db_path}")
