"""
ML-based Signal Detection System
Combines Isolation Forest for anomaly detection + CNN for classification
"""

import json
import numpy as np
from rtlsdr import RtlSdr
import time
import datetime
import pickle
import os
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
            pass
except Exception:
    pass

# Example frequencies and types
FREQUENCIES = [
    (95000000, "wfm"),
    (104000000, "wfm"),
    (49250000, "tv"),
    *[(f, "gsm_nigeria_900") for f in range(935000000, 960000000, 2000000)],
    (446000000, "walkie_pmr446"), (446050000, "walkie_pmr446"), (446100000, "walkie_pmr446"), (446150000, "walkie_pmr446"),
    (140000000, "walkie_vhf"), (150000000, "walkie_vhf"), (160000000, "walkie_vhf"),
    (450000000, "walkie_uhf"), (485000000, "walkie_uhf"),
    (147337500, "dmr")
]

SAMPLE_RATE = 2.048e6
SAMPLES = 256*1024

def collect_samples(freq, label):
    """Collect a single sample at a frequency."""
    # Get device index from environment variable with fallback
    device_index = int(os.getenv('RTL_SDR_DEVICE', '0'))
    try:
        sdr = RtlSdr(device_index=device_index)
    except:
        device_index = 1 if device_index == 0 else 0
        print(f"Trying alternate device index {device_index}...")
        sdr = RtlSdr(device_index=device_index)
    sdr.sample_rate = SAMPLE_RATE
    sdr.center_freq = freq
    sdr.gain = 'auto'
    samples = sdr.read_samples(SAMPLES)
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
    raw_samples = samples[:2048]
    sdr.close()
    return {
        "freq": freq,
        "label": label,
        "peak_power": peak_power,
        "noise_floor": noise_floor,
        "mean_power": mean_power,
        "std_power": std_power,
        "min_power": min_power,
        "max_power": max_power,
        "snr": snr,
        "kurtosis": kurt,
        "skewness": skewness,
        "bandwidth": bandwidth,
        "num_peaks": num_peaks,
        "power_spectrum": base64.b64encode(power.astype(np.float32).tobytes()).decode('utf-8'),
        "raw_samples": base64.b64encode(raw_samples.astype(np.complex64).tobytes()).decode('utf-8'),
        "timestamp": datetime.datetime.now().isoformat()
    }

def collect_training_data(num_samples_per_freq=5, output_file="training_data.json"):
    """
    Collect training data: multiple samples per frequency to build baseline.
    This data will be used to train Isolation Forest and CNN.
    """
    print(f"Collecting {num_samples_per_freq} samples per frequency for training...")
    training_data = []
    for freq, label in FREQUENCIES:
        for i in range(num_samples_per_freq):
            print(f"Collecting {label} at {freq/1e6:.3f} MHz (sample {i+1}/{num_samples_per_freq})...")
            props = collect_samples(freq, label)
            training_data.append(props)
            time.sleep(0.5)
    with open(output_file, "w") as f:
        json.dump(training_data, f, indent=2)
    print(f"Training data saved to {output_file}")
    return training_data

if __name__ == "__main__":
    # Reduced from 10 to 5 samples per frequency to save memory
    collect_training_data(num_samples_per_freq=5)
