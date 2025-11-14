DEVICE_LABEL = "DEVICE_1"  # Change this for each device
DEVICE_LAT = 0.0            # Set device latitude
DEVICE_LONG = 0.0           # Set device longitude

import json
import numpy as np
from rtlsdr import RtlSdr
import time
import datetime
import sqlite3
import struct

# Import scipy functions where needed to avoid import issues
SCIPY_AVAILABLE = False
try:
    from scipy import signal as scipy_signal
    from scipy.stats import kurtosis, skew
    # Test if find_peaks is actually available
    if hasattr(scipy_signal, 'find_peaks'):
        SCIPY_AVAILABLE = True
    else:
        print("Warning: scipy.signal.find_peaks not available, using numpy alternatives")
except ImportError as e:
    print(f"Warning: scipy not available ({e}), using numpy alternatives")
except Exception as e:
    print(f"Warning: scipy import failed ({e}), using numpy alternatives")

SAMPLE_RATE = 2.048e6
SAMPLES = 256*1024
THRESHOLD_DB = 10
SCAN_INTERVAL = 10

# Load baseline
with open("baseline.json") as f:
    baseline = json.load(f)



# Build a list of known signals with their properties
known_signals = [
    {
        "freq": sig["freq"],
        "label": sig["label"],
        "bandwidth": sig["bandwidth"],
        "peak_power": sig.get("peak_power", None),
        "noise_floor": sig.get("noise_floor", None)
    }
    for sig in baseline
]

# Scan frequencies from baseline
FREQUENCIES = [(sig["freq"], sig["label"]) for sig in baseline]



# Signal-type-specific tolerances with frequency-dependent bandwidth
SIGNAL_TOLERANCES = {
    "wfm": {
        "freq_tol": 1000,           # 1 kHz
        "bandwidth_pct": 0.15,      # 15% of frequency
        "peak_power_tol": 8,        # dB
        "noise_floor_tol": 8,       # dB
        "snr_tol": 8,               # dB
        "mean_power_tol": 8,        # dB
        "std_power_tol": 8,         # dB
        "num_peaks_tol": 3
    },
    "tv": {
        "freq_tol": 1000,           # 1 kHz
        "bandwidth_pct": 0.10,      # 10% of frequency
        "peak_power_tol": 10,       # dB
        "noise_floor_tol": 10,      # dB
        "snr_tol": 10,              # dB
        "mean_power_tol": 10,       # dB
        "std_power_tol": 10,        # dB
        "num_peaks_tol": 5
    },
    "gsm_nigeria_900": {
        "freq_tol": 2000,           # 2 kHz
        "bandwidth_pct": 0.10,      # 10% of frequency
        "peak_power_tol": 12,       # dB
        "noise_floor_tol": 12,      # dB
        "snr_tol": 12,              # dB
        "mean_power_tol": 12,       # dB
        "std_power_tol": 12,        # dB
        "num_peaks_tol": 5
    },
    "walkie_pmr446": {
        "freq_tol": 15000,            # 1 kHz
        "bandwidth_pct": 0.7,      # 5% of frequency
        "peak_power_tol": 10,        # dB
        "noise_floor_tol": 10,       # dB
        "snr_tol": 10,               # dB
        "mean_power_tol": 10,        # dB
        "std_power_tol": 10,         # dB
        "num_peaks_tol": 5
    },
    "walkie_vhf": {
        "freq_tol": 1500,           # 1 kHz
        "bandwidth_pct": 0.08,      # 8% of frequency
        "peak_power_tol": 12,        # dB
        "noise_floor_tol": 12,       # dB
        "snr_tol": 12,               # dB
        "mean_power_tol": 12,        # dB
        "std_power_tol": 12,         # dB
        "num_peaks_tol": 6
    },
    "walkie_uhf": {
        "freq_tol": 2000,           # 2 kHz
        "bandwidth_pct": 0.12,      # 12% of frequency
        "peak_power_tol": 10,       # dB
        "noise_floor_tol": 10,      # dB
        "snr_tol": 10,              # dB
        "mean_power_tol": 10,       # dB
        "std_power_tol": 10,        # dB
        "num_peaks_tol": 4
    },
    "dmr": {
        "freq_tol": 2000,           # 2 kHz
        "bandwidth_pct": 0.10,      # 10% of frequency
        "peak_power_tol": 10,       # dB
        "noise_floor_tol": 10,      # dB
        "snr_tol": 10,              # dB
        "mean_power_tol": 10,       # dB
        "std_power_tol": 10,        # dB
        "num_peaks_tol": 4
    }
}

# Default tolerances for unknown signal types
DEFAULT_TOLERANCES = {
    "freq_tol": 2000,
    "bandwidth_pct": 0.10,
    "peak_power_tol": 10,
    "noise_floor_tol": 10,
    "snr_tol": 10,
    "mean_power_tol": 10,
    "std_power_tol": 10,
    "num_peaks_tol": 5
}

def get_tolerances(label, freq):
    """Get tolerances for a signal type, with frequency-dependent bandwidth tolerance."""
    tol = SIGNAL_TOLERANCES.get(label, DEFAULT_TOLERANCES.copy())
    tol_copy = tol.copy()
    tol_copy["bandwidth_tol"] = freq * tol_copy["bandwidth_pct"]
    return tol_copy



def calculate_confidence(measured, baseline_val, tolerance, max_deviation=20):
    """Calculate confidence score (0-100) based on how close measured value is to baseline."""
    if baseline_val is None:
        return 100.0  # No baseline, so accept it
    deviation = abs(measured - baseline_val)
    if deviation <= tolerance:
        return 100.0 - (deviation / tolerance) * 50  # 50-100% confidence
    else:
        deviation_pct = min((deviation / max_deviation) * 100, 100)
        return max(0, 50 - (deviation_pct / 2))  # 0-50% confidence

def find_peaks_numpy(data, height_threshold):
    """Simple peak detection using numpy (fallback for scipy)."""
    if len(data) < 3:
        return np.array([])
    
    peaks = []
    data = np.asarray(data)
    for i in range(1, len(data) - 1):
        if data[i] > data[i-1] and data[i] > data[i+1] and data[i] > height_threshold:
            peaks.append(i)
    return np.array(peaks)

def calculate_kurtosis_numpy(data):
    """Calculate kurtosis using numpy."""
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0.0
    normalized = (data - mean) / std
    return float(np.mean(normalized**4) - 3)

def calculate_skew_numpy(data):
    """Calculate skewness using numpy."""
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0.0
    normalized = (data - mean) / std
    return float(np.mean(normalized**3))

def calculate_advanced_features(samples, power_spectrum, sample_rate):
    """Calculate comprehensive signal features for analysis."""
    features = {}
    
    # Spectral features
    freqs = np.fft.fftfreq(len(power_spectrum), 1/sample_rate)
    power_linear = 10**(power_spectrum/10)
    
    # Spectral centroid (center of mass of spectrum)
    features['spectral_centroid'] = float(np.sum(freqs * power_linear) / np.sum(power_linear)) if np.sum(power_linear) > 0 else 0.0
    
    # Spectral rolloff (frequency below which 85% of energy lies)
    cumsum_power = np.cumsum(power_linear)
    rolloff_threshold = 0.85 * cumsum_power[-1]
    rolloff_idx = np.where(cumsum_power >= rolloff_threshold)[0]
    features['spectral_rolloff'] = float(freqs[rolloff_idx[0]]) if len(rolloff_idx) > 0 else 0.0
    
    # Spectral flux (rate of change in spectrum)
    if len(power_spectrum) > 1:
        spectral_flux = np.sum(np.diff(power_spectrum)**2)
        features['spectral_flux'] = float(spectral_flux)
    else:
        features['spectral_flux'] = 0.0
    
    # Time domain features from I/Q samples
    if len(samples) > 0:
        # Zero crossing rate
        real_part = np.real(samples)
        zero_crossings = np.where(np.diff(np.sign(real_part)))[0]
        features['zero_crossing_rate'] = float(len(zero_crossings) / len(samples))
        
        # Phase and amplitude variance
        phases = np.angle(samples)
        amplitudes = np.abs(samples)
        features['phase_variance'] = float(np.var(phases))
        features['amplitude_variance'] = float(np.var(amplitudes))
        
        # Modulation index estimation
        amplitude_normalized = (amplitudes - np.mean(amplitudes)) / np.std(amplitudes) if np.std(amplitudes) > 0 else amplitudes
        features['modulation_index'] = float(np.std(amplitude_normalized))
    else:
        features['zero_crossing_rate'] = 0.0
        features['phase_variance'] = 0.0
        features['amplitude_variance'] = 0.0
        features['modulation_index'] = 0.0
    
    # Peak analysis (use scipy if available, otherwise numpy fallback)
    try:
        if SCIPY_AVAILABLE:
            peaks, _ = scipy_signal.find_peaks(power_spectrum, height=np.median(power_spectrum) + 6)
        else:
            peaks = find_peaks_numpy(power_spectrum, np.median(power_spectrum) + 6)
    except (AttributeError, NameError):
        # Fallback to numpy implementation if scipy fails
        peaks = find_peaks_numpy(power_spectrum, np.median(power_spectrum) + 6)
    
    if len(peaks) > 0:
        peak_freqs = freqs[peaks[:10]]  # Store up to 10 strongest peaks
        features['peak_frequencies'] = peak_freqs.astype(np.float32).tobytes()
        features['dominant_frequency'] = float(freqs[peaks[np.argmax(power_spectrum[peaks])]])
    else:
        features['peak_frequencies'] = np.array([], dtype=np.float32).tobytes()
        features['dominant_frequency'] = 0.0
    
    # Frequency stability (standard deviation of peak frequencies)
    if len(peaks) > 1:
        features['frequency_stability'] = float(np.std(freqs[peaks]))
    else:
        features['frequency_stability'] = 0.0
    
    return features

def calculate_signal_quality_metrics(power_spectrum, baseline_match, measured_features):
    """Calculate signal quality and confidence metrics."""
    metrics = {}
    
    # Signal quality index (combination of SNR, bandwidth efficiency, stability)
    snr = measured_features.get('snr', 0)
    bandwidth = measured_features.get('bandwidth', 1)
    freq_stability = measured_features.get('frequency_stability', 0)
    
    # Bandwidth efficiency (signal power relative to bandwidth)
    peak_power = measured_features.get('peak_power', 0)
    noise_floor = measured_features.get('noise_floor', 0)
    signal_power = peak_power - noise_floor
    bandwidth_efficiency = signal_power / np.log10(max(bandwidth, 1)) if bandwidth > 0 else 0
    metrics['bandwidth_efficiency'] = float(bandwidth_efficiency)
    
    # Signal quality index (0-100)
    quality_components = [
        min(snr / 20, 1) * 40,  # SNR component (max 40 points)
        min(bandwidth_efficiency / 10, 1) * 30,  # Efficiency component (max 30 points)
        max(0, 1 - freq_stability / 1000) * 30  # Stability component (max 30 points)
    ]
    metrics['signal_quality_index'] = float(sum(quality_components))
    
    # Interference level estimation
    if len(power_spectrum) > 10:
        # Look for multiple peaks indicating interference
        if SCIPY_AVAILABLE:
            peaks, _ = scipy_signal.find_peaks(power_spectrum, height=np.median(power_spectrum) + 3)
        else:
            # Use numpy fallback for peak detection
            peaks = find_peaks_numpy(power_spectrum, np.median(power_spectrum) + 3)
        interference_score = min(len(peaks) / 5, 1) * 100  # More peaks = more interference
        metrics['interference_level'] = float(interference_score)
    else:
        metrics['interference_level'] = 0.0
    
    return metrics

def create_bar_graph(value, min_val, max_val, width=8):
    """Create compact ASCII bar graph."""
    if max_val == min_val:
        return "█" * width
    ratio = max(0, min(1, (value - min_val) / (max_val - min_val)))
    filled = int(ratio * width)
    empty = width - filled
    return "█" * filled + "░" * empty

def print_compact_detection(timestamp, freq, label, device_label, peak_power, snr, bandwidth, confidence):
    """Print single line detection with key info."""
    time_str = timestamp.strftime('%H:%M:%S')
    conf_bar = create_bar_graph(confidence, 0, 100, 6)
    print(f"🔔 {time_str} | {freq/1e6:8.3f}MHz | {label[:12]:<12} | Peak:{peak_power:5.1f}dB SNR:{snr:5.1f}dB BW:{bandwidth:5.0f}Hz | {confidence:5.1f}% {conf_bar}")

def print_mini_spectrum(power, noise_floor, width=30):
    """Print ultra-compact power spectrum."""
    # Heavily downsample for mini display
    downsample = max(1, len(power) // width)
    power_mini = power[::downsample][:width]
    normalized = np.maximum(power_mini - noise_floor, 0)
    max_power = np.max(normalized) if len(normalized) > 0 and np.max(normalized) > 0 else 1
    
    spectrum_line = ""
    for p in normalized:
        height = int((p / max_power) * 4) if max_power > 0 else 0
        chars = [" ", "▁", "▃", "▅", "█"]
        spectrum_line += chars[min(height, 4)]
    
    return f"📊[{spectrum_line}]"

def print_comparison_compact(measured, baseline, tolerances):
    """Print compact baseline comparison."""
    if baseline is None:
        return ""
    
    status_chars = []
    for param in ['peak_power', 'snr', 'bandwidth']:
        if param in baseline and param in measured:
            baseline_val = baseline[param]
            measured_val = measured[param]
            tolerance = tolerances.get(param + '_tol', 0)
            deviation = abs(measured_val - baseline_val)
            within_tolerance = deviation <= tolerance
            status_chars.append("✓" if within_tolerance else "✗")
    
    return f"Baseline: {''.join(status_chars)} " if status_chars else ""

def listen_and_flag():
    """Main listening function with enhanced console output."""
    sdr = RtlSdr(device_index=1)  # Specify device index if multiple SDRs are connected
    sdr.sample_rate = SAMPLE_RATE
    sdr.gain = 'auto'
    conn = sqlite3.connect('detections.db')
    
    # For waterfall: keep a rolling buffer of FFTs per frequency
    fft_history = {}
    max_history = 64  # Number of FFTs to keep for waterfall (64 = ~10 minutes @ 10s intervals)
    
    # Enhanced tracking variables
    scan_count = 0
    detection_count = 0
    detection_sequence = 0
    last_detection_time = {}
    frequency_history = {}  # Track frequency changes over time for Doppler analysis
    
    print(f"🛰️  RTL-SDR LISTENER | Device: {DEVICE_LABEL} | {len(FREQUENCIES)} freqs | {SAMPLE_RATE/1e6:.1f}MHz | {SCAN_INTERVAL}s interval")
    
    try:
        while True:
            scan_count += 1
            scan_time = datetime.datetime.now()
            
            for freq, label in FREQUENCIES:
                sdr.center_freq = freq
                samples = sdr.read_samples(SAMPLES)
                
                # Store a short segment of raw samples
                raw_samples = samples[:2048]
                
                # FFT for this sweep
                power = 10 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples)))**2)
                
                # Waterfall: update FFT history
                if freq not in fft_history:
                    fft_history[freq] = []
                fft_history[freq].append(power.astype(np.float32))
                if len(fft_history[freq]) > max_history:
                    fft_history[freq].pop(0)
                
                # Basic features
                peak_power = float(np.max(power))
                noise_floor = float(np.median(power))
                mean_power = float(np.mean(power))
                std_power = float(np.std(power))
                min_power = float(np.min(power))
                max_power = float(np.max(power))
                snr = peak_power - noise_floor
                
                # Use scipy if available, otherwise numpy fallback
                try:
                    if SCIPY_AVAILABLE:
                        kurt = float(kurtosis(power))
                        skewness = float(skew(power))
                    else:
                        kurt = calculate_kurtosis_numpy(power)
                        skewness = calculate_skew_numpy(power)
                except (AttributeError, NameError):
                    # Fallback to numpy implementations
                    kurt = calculate_kurtosis_numpy(power)
                    skewness = calculate_skew_numpy(power)
                bandwidth = float(np.sum(power > noise_floor + 6) * (SAMPLE_RATE / SAMPLES))
                peaks = np.where(power > noise_floor + 6)[0]
                num_peaks = int(len(peaks))
                
                # Calculate advanced features with error handling
                try:
                    advanced_features = calculate_advanced_features(raw_samples, power, SAMPLE_RATE)
                except Exception as e:
                    print(f"Warning: Failed to calculate advanced features: {e}")
                    # Provide default values
                    advanced_features = {
                        'spectral_centroid': 0.0,
                        'spectral_rolloff': 0.0,
                        'spectral_flux': 0.0,
                        'zero_crossing_rate': 0.0,
                        'peak_frequencies': np.array([], dtype=np.float32).tobytes(),
                        'modulation_index': 0.0,
                        'phase_variance': 0.0,
                        'amplitude_variance': 0.0,
                        'dominant_frequency': 0.0,
                        'frequency_stability': 0.0
                    }
                
                # Calculate signal quality metrics
                measured_features = {
                    'snr': snr, 'bandwidth': bandwidth, 'peak_power': peak_power,
                    'noise_floor': noise_floor, 'frequency_stability': advanced_features['frequency_stability']
                }
                quality_metrics = calculate_signal_quality_metrics(power, None, measured_features)
                
                # Track frequency changes for Doppler analysis
                if freq not in frequency_history:
                    frequency_history[freq] = []
                frequency_history[freq].append((scan_time, freq))
                if len(frequency_history[freq]) > 10:  # Keep last 10 measurements
                    frequency_history[freq].pop(0)
                
                # Calculate Doppler shift estimation
                doppler_shift = 0.0
                if len(frequency_history[freq]) > 1:
                    freq_changes = [f[1] for f in frequency_history[freq]]
                    if len(freq_changes) > 1:
                        doppler_shift = float(np.std(freq_changes))
                
                # Center frequency offset from nominal
                center_freq_offset = float(freq - sdr.center_freq) if hasattr(sdr, 'center_freq') else 0.0
                
                # Activity score (combination of power and stability)
                activity_score = min(100, (snr / 10) * (1 / max(advanced_features['frequency_stability'] / 1000, 0.1)))
                
                # Check if this signal matches any in the baseline
                match_found = False
                baseline_match = None
                tol = get_tolerances(label, freq)
                
                for sig in known_signals:
                    if label == sig["label"]:
                        if (
                            abs(freq - sig["freq"]) <= tol["freq_tol"]
                            and abs(bandwidth - sig.get("bandwidth", bandwidth)) <= tol["bandwidth_tol"]
                            and (sig.get("peak_power") is None or abs(peak_power - sig["peak_power"]) <= tol["peak_power_tol"])
                            and (sig.get("noise_floor") is None or abs(noise_floor - sig["noise_floor"]) <= tol["noise_floor_tol"])
                            and (sig.get("snr") is None or abs(snr - sig["snr"]) <= tol["snr_tol"])
                            and (sig.get("mean_power") is None or abs(mean_power - sig["mean_power"]) <= tol["mean_power_tol"])
                            and (sig.get("std_power") is None or abs(std_power - sig["std_power"]) <= tol["std_power_tol"])
                            and (sig.get("num_peaks") is None or abs(num_peaks - sig["num_peaks"]) <= tol["num_peaks_tol"])
                        ):
                            match_found = True
                            baseline_match = sig
                            break
                
                if not match_found:
                    detection_count += 1
                    
                    # Calculate confidence scores
                    confidence_scores = {}
                    overall_confidence = 0
                    
                    if baseline_match:
                        confidence_scores['peak_power'] = calculate_confidence(peak_power, baseline_match.get('peak_power'), tol.get('peak_power_tol', 10))
                        confidence_scores['snr'] = calculate_confidence(snr, baseline_match.get('snr'), tol.get('snr_tol', 10))
                        confidence_scores['bandwidth'] = calculate_confidence(bandwidth, baseline_match.get('bandwidth'), tol.get('bandwidth_tol', 1000))
                        overall_confidence = np.mean(list(confidence_scores.values()))
                    else:
                        overall_confidence = 75.0  # Default confidence for new detections
                    
                    # Print compact detection
                    print_compact_detection(scan_time, freq, label, DEVICE_LABEL, peak_power, snr, bandwidth, overall_confidence)
                    
                    # Add mini spectrum and baseline status
                    spectrum_mini = print_mini_spectrum(power, noise_floor, width=20)
                    baseline_status = print_comparison_compact({'peak_power': peak_power, 'snr': snr, 'bandwidth': bandwidth}, baseline_match, tol)
                    print(f"    {spectrum_mini} {baseline_status}Peaks:{num_peaks} Kurt:{kurt:.1f}")
                    
                    # Save to database (essential data only)
                    c = conn.cursor()
                    # Downsample FFT history for waterfall (reduce from 262k to 512 points per sweep)
                    waterfall_data = None
                    if len(fft_history[freq]) >= 2:  # Need at least 2 sweeps for waterfall
                        fft_stack = np.stack(fft_history[freq])
                        # Downsample each sweep to 512 points
                        step = max(1, fft_stack.shape[1] // 512)
                        waterfall_downsampled = fft_stack[:, ::step][:, :512]
                        waterfall_data = waterfall_downsampled.astype(np.float32).tobytes()
                    
                    # Store lightweight power spectrum (downsampled to 512 points)
                    power_spectrum_downsampled = None
                    if len(power) > 512:
                        step = len(power) // 512
                        power_spectrum_downsampled = power[::step][:512].astype(np.float32).tobytes()
                    else:
                        power_spectrum_downsampled = power.astype(np.float32).tobytes()
                    
                    # Store only a small raw sample segment for analysis (2048 samples = ~8KB)
                    raw_samples_light = raw_samples.astype(np.complex64).tobytes()
                    
                    # Calculate signal duration (time since first detection of this signal)
                    signal_key = f"{freq}_{label}"
                    if signal_key not in last_detection_time:
                        last_detection_time[signal_key] = scan_time
                        signal_duration = 0.0
                    else:
                        signal_duration = (scan_time - last_detection_time[signal_key]).total_seconds()
                    
                    # Calculate baseline deviation if baseline exists
                    baseline_deviation = 0.0
                    if baseline_match:
                        deviations = []
                        if baseline_match.get('peak_power'):
                            deviations.append(abs(peak_power - baseline_match['peak_power']))
                        if baseline_match.get('bandwidth'):
                            deviations.append(abs(bandwidth - baseline_match['bandwidth']) / 1000)  # Normalize
                        baseline_deviation = float(np.mean(deviations)) if deviations else 0.0
                    
                    detection_sequence += 1
                    
                    c.execute('''
                        INSERT INTO detections (
                            timestamp, freq, label, bandwidth, peak_power, noise_floor, snr,
                            mean_power, std_power, min_power, max_power, kurtosis, skewness, num_peaks,
                            power_spectrum, device_label, device_lat, device_long, raw_samples, fft_history,
                            confidence_score, signal_duration, center_freq_offset, bandwidth_efficiency,
                            spectral_centroid, spectral_rolloff, spectral_flux, zero_crossing_rate,
                            peak_frequencies, modulation_index, phase_variance, amplitude_variance,
                            dominant_frequency, frequency_stability, scan_number, detection_sequence,
                            baseline_deviation, signal_quality_index, interference_level, doppler_shift, activity_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        scan_time.isoformat(), freq, label, bandwidth, peak_power, noise_floor, snr,
                        mean_power, std_power, min_power, max_power, kurt, skewness, num_peaks,
                        power_spectrum_downsampled, DEVICE_LABEL, DEVICE_LAT, DEVICE_LONG, 
                        raw_samples_light, waterfall_data,
                        overall_confidence, signal_duration, center_freq_offset, quality_metrics['bandwidth_efficiency'],
                        advanced_features['spectral_centroid'], advanced_features['spectral_rolloff'], 
                        advanced_features['spectral_flux'], advanced_features['zero_crossing_rate'],
                        advanced_features['peak_frequencies'], advanced_features['modulation_index'],
                        advanced_features['phase_variance'], advanced_features['amplitude_variance'],
                        advanced_features['dominant_frequency'], advanced_features['frequency_stability'],
                        scan_count, detection_sequence, baseline_deviation, quality_metrics['signal_quality_index'],
                        quality_metrics['interference_level'], doppler_shift, activity_score
                    ))
                    conn.commit()
                    
                    print(f"\n✅ Saved to database. Total detections: {detection_count}")
            
            # Compact scan status
            if detection_count == 0:
                print(f"⏱️  Scan #{scan_count} @ {scan_time.strftime('%H:%M:%S')} - {len(FREQUENCIES)} freqs monitored, no new signals")
            time.sleep(SCAN_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n" + "="*100)
        print("🛑 LISTENER STOPPED BY USER")
        print(f"Total scans: {scan_count} | Total detections: {detection_count}")
        print("="*100 + "\n")
        conn.close()

if __name__ == "__main__":
    listen_and_flag()
