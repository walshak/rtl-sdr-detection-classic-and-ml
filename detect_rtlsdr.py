#!/usr/bin/env python3
"""
RTL-SDR Device Detection Utility
Helps identify which device index to use for your RTL-SDR
"""

from rtlsdr import RtlSdr
import sys

def test_device(index):
    """Try to open and test an RTL-SDR device at the given index."""
    try:
        print(f"\nTesting device index {index}...")
        sdr = RtlSdr(device_index=index)
        
        # Get device info
        print(f"  [OK] Device found at index {index}")
        print(f"  Tuner type: {sdr.get_tuner_type()}")
        print(f"  Gains available: {sdr.get_gains()}")
        
        # Test basic operation
        sdr.sample_rate = 2.048e6
        sdr.center_freq = 100e6
        sdr.gain = 'auto'
        
        samples = sdr.read_samples(1024)
        print(f"  Successfully read {len(samples)} samples")
        print(f"  [SUCCESS] Device index {index} is working!")
        
        sdr.close()
        return True
        
    except Exception as e:
        print(f"  [FAIL] Device index {index} not accessible: {e}")
        return False

def main():
    print("=" * 60)
    print("RTL-SDR Device Detection")
    print("=" * 60)
    
    found_devices = []
    
    # Test indices 0-3 (most systems will have 0 or 1)
    for index in range(4):
        if test_device(index):
            found_devices.append(index)
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if found_devices:
        print(f"\n[SUCCESS] Found {len(found_devices)} RTL-SDR device(s):")
        for idx in found_devices:
            print(f"  - Device index: {idx}")
        
        recommended = found_devices[0]
        print(f"\nRecommended configuration:")
        print(f"  Set RTL_SDR_DEVICE={recommended} in your .env file")
        print(f"\nOr run this command:")
        print(f"  set RTL_SDR_DEVICE={recommended}")
        
        # Try to update .env file
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
            
            if 'RTL_SDR_DEVICE=' in env_content:
                import re
                new_content = re.sub(
                    r'RTL_SDR_DEVICE=\d+',
                    f'RTL_SDR_DEVICE={recommended}',
                    env_content
                )
                with open('.env', 'w') as f:
                    f.write(new_content)
                print(f"\n[AUTO-CONFIGURED] Updated .env file with RTL_SDR_DEVICE={recommended}")
        except:
            pass
            
    else:
        print("\n[ERROR] No RTL-SDR devices found!")
        print("\nTroubleshooting:")
        print("  1. Make sure RTL-SDR device is plugged in")
        print("  2. Install RTL-SDR drivers (Zadig on Windows)")
        print("  3. Check USB connection")
        print("  4. Try a different USB port")
        print("  5. Restart the computer")
        sys.exit(1)
    
    print()

if __name__ == "__main__":
    main()
