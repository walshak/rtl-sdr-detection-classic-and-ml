import sqlite3

def init_db():
    conn = sqlite3.connect('detections.db')
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

if __name__ == "__main__":
    init_db()
    print("detections.db initialized.")
