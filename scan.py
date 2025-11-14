import numpy as np
from rtlsdr import RtlSdr
import time
import datetime

# Frequency bands in Hz
BANDS = {
    'GSM900': (880e6, 915e6),
    'VHF': (136e6, 174e6),
    'UHF': (400e6, 520e6)
}

SAMPLE_RATE = 2.048e6  # Hz
SAMPLES = 256*1024
THRESHOLD = 10  # dB above noise floor
SCAN_INTERVAL = 10  # seconds between scans

# Store seen signals
seen_signals = set()

def scan_band(sdr, band_name, freq_start, freq_end, step=2e6):
    detected = []
    freq = freq_start
    while freq < freq_end:
        sdr.center_freq = freq
        samples = sdr.read_samples(SAMPLES)
        power = 10 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples)))**2)
        freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), 1/SAMPLE_RATE)) + freq
        noise_floor = np.median(power)
        peaks = np.where(power > noise_floor + THRESHOLD)[0]
        for p in peaks:
            detected_freq = freqs[p]
            detected.append(round(detected_freq/1e3)*1e3)  # Round to kHz
        freq += step
    return set(detected)

def main():
    global seen_signals
    sdr = RtlSdr(device_index=1)  # Specify device index if multiple SDRs are connected
    sdr.sample_rate = SAMPLE_RATE
    sdr.gain = 'auto'
    print('Starting scan...')
    while True:
        new_signals = set()
        for band, (f_start, f_end) in BANDS.items():
            print(f'Scanning {band}...')
            detected = scan_band(sdr, band, f_start, f_end)
            for freq in detected:
                if freq not in seen_signals:
                    print(f'[{datetime.datetime.now()}] New signal detected: {band} {freq/1e6:.3f} MHz')
                    with open('signals.log', 'a') as log:
                        log.write(f'{datetime.datetime.now()}, {band}, {freq/1e6:.3f} MHz\n')
                    new_signals.add(freq)
        seen_signals.update(new_signals)
        print('Scan complete. Waiting...')
        time.sleep(SCAN_INTERVAL)

if __name__ == '__main__':
    main()
