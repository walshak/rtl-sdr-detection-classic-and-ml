import json
import numpy as np
from rtlsdr import RtlSdr
import time
import datetime
import os
import sys
import signal

# Example frequencies and types
FREQUENCIES = [
    (95000000, "wfm"),
    (104000000, "wfm"),
    (49250000, "tv"),
    # GSM Nigeria (downlink bands)
    *[(f, "gsm_nigeria_900") for f in range(935000000, 960000000, 2000000)],
    # Walkie-talkie frequencies - PMR446 band
    (446000000, "walkie_pmr446"), (446050000, "walkie_pmr446"), (446100000, "walkie_pmr446"), (446150000, "walkie_pmr446"),
    # Walkie-talkie frequencies - VHF band
    (140000000, "walkie_vhf"), (150000000, "walkie_vhf"), (160000000, "walkie_vhf"),
    # Walkie-talkie frequencies - UHF band
    (450000000, "walkie_uhf"), (485000000, "walkie_uhf"),
    # DMR
    (147337500, "dmr")
]

SAMPLE_RATE = 2.048e6
SAMPLES = 256*1024



def collect_samples(freq, label):
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
    snr = peak_power - noise_floor
    bandwidth = float(np.sum(power > noise_floor + 6) * (SAMPLE_RATE / SAMPLES))
    peaks = np.where(power > noise_floor + 6)[0]
    num_peaks = int(len(peaks))
    sdr.close()
    return {
        "freq": freq,
        "label": label,
        "peak_power": peak_power,
        "noise_floor": noise_floor,
        "bandwidth": bandwidth,
        "snr": snr,
        "mean_power": mean_power,
        "std_power": std_power,
        "num_peaks": num_peaks,
        "timestamp": datetime.datetime.now().isoformat()
    }


def main():
    baseline = []
    baseline_file = "baseline.json"
    interrupted = False
    
    def signal_handler(sig, frame):
        """Handle Ctrl+C gracefully"""
        nonlocal interrupted
        interrupted = True
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Load existing baseline if it exists
    if os.path.exists(baseline_file):
        try:
            with open(baseline_file, "r") as f:
                baseline = json.load(f)
            print(f"Loaded {len(baseline)} existing baseline entries")
        except:
            print("Starting fresh baseline collection")
    
    total_freqs = len(FREQUENCIES)
    print(f"\nBaseline Collection - {total_freqs} frequencies")
    print("=" * 50)
    print("Press Ctrl+C at any time to stop and save current progress")
    print("=" * 50)
    print()
    
    def save_baseline():
        """Save current baseline to file"""
        with open(baseline_file, "w") as f:
            json.dump(baseline, f, indent=2)
        print(f"\n✓ Saved {len(baseline)} entries to {baseline_file}")
    
    try:
        for i, (freq, label) in enumerate(FREQUENCIES, 1):
            # Check for interrupt
            if interrupted:
                print(f"\n\n⏭️  Stopped by user at {i}/{total_freqs}")
                save_baseline()
                return
            
            print(f"[{i}/{total_freqs}] Collecting {label} at {freq/1e6:.3f} MHz...", end=" ", flush=True)
            
            try:
                props = collect_samples(freq, label)
                baseline.append(props)
                print("✓")
                
                # Auto-save every 10 items
                if len(baseline) % 10 == 0:
                    save_baseline()
                
            except Exception as e:
                print(f"✗ Error: {e}")
                continue
            
            # Short delay between samples
            time.sleep(0.5)
        
        # Final save
        save_baseline()
        print("\n" + "=" * 50)
        print("Baseline collection complete!")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrupted by user at {len(baseline)}/{total_freqs}")
        save_baseline()
    except Exception as e:
        print(f"\n\n❌ Error during collection: {e}")
        if baseline:
            save_baseline()

if __name__ == "__main__":
    main()
