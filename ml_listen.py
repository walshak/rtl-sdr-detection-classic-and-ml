"""
ML-based Listen: Uses trained models for anomaly detection + classification
Replaces static tolerance-based detection with ML models.
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF warnings

import json
import numpy as np
from rtlsdr import RtlSdr
import time
import datetime
import sqlite3
import pickle
from keras.models import load_model
from keras.backend import clear_session
import base64

# Configure GPU memory limiting (2GB max)
try:
    import tensorflow as tf
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            tf.config.set_logical_device_configuration(
                gpus[0],
                [tf.config.LogicalDeviceConfiguration(memory_limit=2048)]  # 2GB limit
            )
        except RuntimeError:
            pass  # Silently continue if GPU config fails
except Exception:
    pass  # Silently continue if TF not available

DEVICE_LABEL = "DEVICE_1"
DEVICE_LAT = 0.0
DEVICE_LONG = 0.0

SAMPLE_RATE = 2.048e6
SAMPLES = 256*1024
SCAN_INTERVAL = 10

# Load baseline from training data
print("Loading training data as baseline...")
with open("training_data.json") as f:
    training_data = json.load(f)

# Load trained models
print("Loading trained models...")
with open("iso_forest_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
with open("iso_forest_model.pkl", "rb") as f:
    iso_forest = pickle.load(f)

# Load CNN model (handle both .h5 and split architecture+weights formats)
try:
    cnn_model = load_model("cnn_classifier.h5")
    print("✓ Loaded CNN model from cnn_classifier.h5")
except Exception as e:
    print(f"Note: Could not load cnn_classifier.h5, trying split format...")
    try:
        import json
        with open("cnn_classifier_architecture.json", "r") as json_file:
            model_json = json_file.read()
        from keras.models import model_from_json
        cnn_model = model_from_json(model_json)
        cnn_model.load_weights("cnn_classifier_weights.h5")
        print("✓ Loaded CNN model from architecture (JSON) + weights (H5)")
    except Exception as e2:
        print(f"ERROR: Could not load CNN model: {e}\n{e2}")
        print("Please run ml_training.py first to generate the trained model.")
        exit(1)

with open("label_to_idx.pkl", "rb") as f:
    label_to_idx = pickle.load(f)

idx_to_label = {v: k for k, v in label_to_idx.items()}

# Determine max spectrum length
power_spectra = []
for d in training_data:
    arr = np.frombuffer(base64.b64decode(d["power_spectrum"]), dtype=np.float32)
    power_spectra.append(arr)
max_spectrum_len = max(len(p) for p in power_spectra)

# Scan frequencies from training data (baseline)
FREQUENCIES = [(d["freq"], d["label"]) for d in training_data]
FREQUENCIES = list(set(FREQUENCIES))  # Remove duplicates

print(f"Loaded baseline with {len(training_data)} samples")
print(f"Models loaded. Scanning {len(FREQUENCIES)} unique frequencies.")

def extract_features(samples, freq, label):
    """Extract feature vector for anomaly detection."""
    power = 10 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples)))**2)
    peak_power = float(np.max(power))
    noise_floor = float(np.median(power))
    mean_power = float(np.mean(power))
    std_power = float(np.std(power))
    min_power = float(np.min(power))
    max_power = float(np.max(power))
    snr = peak_power - noise_floor
    from scipy.stats import kurtosis, skew
    kurt = float(kurtosis(power))
    skewness = float(skew(power))
    bandwidth = float(np.sum(power > noise_floor + 6) * (SAMPLE_RATE / SAMPLES))
    peaks = np.where(power > noise_floor + 6)[0]
    num_peaks = int(len(peaks))
    return {
        "power": power,
        "features": np.array([peak_power, noise_floor, mean_power, std_power, min_power, max_power, snr, kurt, skewness, bandwidth, num_peaks]),
        "peak_power": peak_power,
        "noise_floor": noise_floor,
        "snr": snr,
        "bandwidth": bandwidth,
        "num_peaks": num_peaks,
        "kurtosis": kurt,
        "skewness": skewness,
        "mean_power": mean_power,
        "std_power": std_power,
        "min_power": min_power,
        "max_power": max_power
    }

def is_anomaly(features_vec):
    """Check if signal is anomalous using Isolation Forest."""
    features_scaled = scaler.transform([features_vec])
    prediction = iso_forest.predict(features_scaled)[0]
    return prediction == -1  # -1 = anomaly

def classify_signal(power_spectrum):
    """Classify signal using CNN."""
    # Pad spectrum to match training length
    padded = np.pad(power_spectrum, (0, max_spectrum_len - len(power_spectrum)), mode='constant')
    # Normalize
    padded = (padded - np.mean(padded)) / (np.std(padded) + 1e-8)
    padded = padded.reshape((1, max_spectrum_len, 1))
    # Predict
    pred = cnn_model.predict(padded, verbose=0)
    pred_label = idx_to_label[np.argmax(pred)]
    confidence = np.max(pred)
    return pred_label, confidence

def listen_and_flag():
    # Get device index from environment variable with fallback
    device_index = int(os.getenv('RTL_SDR_DEVICE', '0'))
    try:
        sdr = RtlSdr(device_index=device_index)
        print(f"Using RTL-SDR device at index {device_index}")
    except:
        device_index = 1 if device_index == 0 else 0
        print(f"Trying alternate device index {device_index}...")
        sdr = RtlSdr(device_index=device_index)
    sdr.sample_rate = SAMPLE_RATE
    sdr.gain = 'auto'
    
    # Use data folder for database
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    db_path = os.path.join(data_dir, 'detections_ml.db')
    conn = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    
    fft_history = {}
    max_history = 32
    
    while True:
        for freq, label in FREQUENCIES:
            sdr.center_freq = freq
            samples = sdr.read_samples(SAMPLES)
            
            # Extract features
            result = extract_features(samples, freq, label)
            power = result["power"]
            features_vec = result["features"]
            
            # Anomaly detection
            anomaly = is_anomaly(features_vec)
            
            if anomaly:
                # Further classify with CNN
                pred_label, confidence = classify_signal(power)
                
                print(f"[{datetime.datetime.now()}] ANOMALY DETECTED: {label} @ {freq/1e6:.3f} MHz")
                print(f"  Isolation Forest: Anomaly")
                print(f"  CNN Classification: {pred_label} (confidence: {confidence:.2%})")
                print(f"  Peak Power: {result['peak_power']:.1f} dB, SNR: {result['snr']:.1f} dB, Bandwidth: {result['bandwidth']:.1f} Hz")
                
                # Save detection
                c = conn.cursor()
                c.execute('''
                    INSERT INTO detections_ml (
                        timestamp, freq, label, peak_power, noise_floor, snr, bandwidth, 
                        kurtosis, skewness, num_peaks, power_spectrum,
                        device_label, device_lat, device_long, raw_samples,
                        iso_forest_anomaly, cnn_predicted_label, cnn_confidence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.datetime.now().isoformat(), freq, label, 
                    result['peak_power'], result['noise_floor'], result['snr'], result['bandwidth'],
                    result['kurtosis'], result['skewness'], result['num_peaks'], power.astype(np.float32).tobytes(),
                    DEVICE_LABEL, DEVICE_LAT, DEVICE_LONG, samples[:2048].astype(np.complex64).tobytes(),
                    True, pred_label, confidence
                ))
                conn.commit()
        
        print(f"Scan complete. Waiting {SCAN_INTERVAL}s...")
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    listen_and_flag()
