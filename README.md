# RTL-SDR ML Signal Detection System

An advanced software-defined radio (SDR) system that uses machine learning to detect, classify, and visualize RF signals across multiple bands. Features anomaly detection, CNN-based signal classification, and an interactive web dashboard.

## 🚀 Features

### Core Detection
- **Multi-band scanning**: GSM 900, VHF, UHF, ISM, and custom frequency ranges
- **Signal fingerprinting**: Automatic detection of WFM, TV, GSM, walkie-talkie, DMR, etc.
- **Rich feature extraction**: Bandwidth, SNR, peak power, noise floor, signal quality metrics
- **Memory-optimized storage**: 99% reduction in storage requirements while preserving visualization data

### Machine Learning
- **Isolation Forest**: Anomaly detection to identify unusual signal patterns
- **CNN Classifier**: Deep learning model for automatic signal type classification
- **Confidence scoring**: ML confidence levels for each detection
- **GPU optimization**: Memory-limited training (2GB VRAM) with fallback options

### Visualization & API
- **Interactive dashboard**: Device selection, detection tables, and real-time charts
- **12+ chart types**: Spectrum, waterfall, scatter, timeline, histogram, signal quality, etc.
- **REST API**: Comprehensive endpoints for data access and chart generation
- **Real-time monitoring**: Live updates with compact console output

### User Experience
- **Enhanced console output**: Compact single-line detection display with confidence scores
- **Mini spectrum visualization**: ASCII-based spectrum plots in terminal
- **Web dashboard**: Intuitive interface with device selection and multi-chart views
- **Responsive design**: Tailwind CSS with mobile-friendly layout

## 📋 Requirements

### Hardware
- **RTL-SDR USB dongle** (RTL2832U-based)
- **Antenna**: Appropriate for target frequencies
- **USB 2.0/3.0 port**

### Software
- **Python 3.7–3.11** (Python 3.12+ may have compatibility issues)
- **Windows 10/11** with PowerShell (primary platform)
- **Zadig driver** for RTL-SDR (Windows only)
- **GPU support** (optional, for ML training acceleration)

### Dependencies
```
pyrtlsdr          # RTL-SDR interface
numpy             # Numerical computations
matplotlib        # Plotting and visualization
scipy             # Signal processing
flask             # Web API framework
scikit-learn      # Machine learning (Isolation Forest)
tensorflow-gpu    # Deep learning (CNN classification)
```

## 🛠️ Installation & Setup

### 1. Hardware Setup
```powershell
# Plug in your RTL-SDR dongle
# Install Zadig driver from https://zadig.akeo.ie/
# Select your RTL-SDR device and install WinUSB driver
```

### 2. Python Environment
```powershell
# Install Python 3.7-3.11 (recommended: 3.9 or 3.10)
python --version

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Verify activation (should show venv path)
where python
```

### 3. Install Dependencies
```powershell
# Install all required packages
pip install -r requirements.txt

# Verify RTL-SDR installation
python -c "import rtlsdr; print('RTL-SDR installed successfully')"
```

### 4. Database Initialization
```powershell
# Initialize main detection database (optimized schema)
python init_db.py

# Initialize ML detection database (if using ML features)
python init_ml_db.py
```

## 🏃‍♂️ Quick Start

### Basic Signal Detection
```powershell
# Start basic signal detection (recommended first run)
python listen.py

# Expected output:
# ┌─ RTL-SDR Signal Detection ─────────────────────────────────────┐
# │ Device: 0 | Gain: 49.6dB | Rate: 2.048MHz | Started: 14:30:15 │
# └─────────────────────────────────────────────────────────────────┘
# 
# [14:30:17] 📡 433.920MHz │ FM     │ BW:0.2M │ SNR:15dB │ ████▌     │ 85%
# [14:30:19] 📻 145.500MHz │ NFM    │ BW:0.1M │ SNR:22dB │ ██████▌   │ 92%
```

### Web Dashboard
```powershell
# Start the web API and dashboard
python api.py

# Open browser to: http://localhost:5000/
# - Select your RTL-SDR device
# - View last 100 detections in table
# - Interactive charts: waterfall, spectrum, features
```

## 🧠 Machine Learning Setup (Advanced)

### 1. Collect Training Data
```powershell
# Collect baseline data for ML training (15-20 minutes)
python ml_data_collection.py

# Output: training_data.json (~5-10 MB)
# Samples: 10 per frequency across full spectrum
```

### 2. Train ML Models
```powershell
# Train Isolation Forest + CNN (2-5 minutes)
python ml_training.py

# Generated files:
# - iso_forest_model.pkl      (anomaly detector)
# - iso_forest_scaler.pkl     (feature scaler)
# - cnn_classifier.h5         (CNN classifier)
# - label_to_idx.pkl          (label mappings)
# - training_history.png      (training curves)
```

### 3. ML-Enhanced Detection
```powershell
# Run ML-enhanced detection
python ml_listen.py

# Features:
# - Anomaly detection with confidence scores
# - Automatic signal classification
# - ML-based filtering and prioritization
```

## 📊 API Endpoints

### Detection Data
- `GET /detections` - List all detections (paginated)
- `GET /detections/<id>` - Get specific detection
- `DELETE /detections/<id>` - Delete detection
- `GET /devices` - List available RTL-SDR devices

### Chart Data
- `GET /chart/spectrum/<id>` - Power spectrum chart
- `GET /chart/waterfall` - Waterfall diagram
- `GET /chart/timeline` - Detection timeline
- `GET /chart/scatter` - Frequency vs SNR scatter
- `GET /chart/histogram` - Signal distribution
- `GET /chart/features` - Feature analysis
- `GET /chart/signal_strength` - Signal strength over time
- `GET /chart/frequency_distribution` - Frequency usage
- `GET /chart/signal_quality` - Quality metrics
- `GET /chart/peaks` - Peak detection analysis

### Parameters
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: varies by chart)
- `device_id` - Filter by device (optional)

## 🎛️ Configuration

### Signal Detection Parameters
```python
# listen.py configuration
FREQUENCY_RANGES = [
    (88e6, 108e6),      # FM Radio
    (144e6, 148e6),     # VHF Amateur
    (430e6, 440e6),     # UHF Amateur
    (902e6, 928e6),     # ISM Band
]

SCAN_STEP = 100000      # 100 kHz steps
SAMPLE_RATE = 2048000   # 2.048 MHz
GAIN = 'auto'           # Automatic gain control
```

### ML Training Parameters
```python
# ml_training.py configuration
ISOLATION_FOREST_CONTAMINATION = 0.1    # Expected anomaly rate
CNN_EPOCHS = 20                         # Training epochs
BATCH_SIZE = 4                          # Memory-optimized batch size
GPU_MEMORY_LIMIT = 2048                 # 2GB VRAM limit
```

### Database Schema
```sql
-- Optimized detection storage
CREATE TABLE detections (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    frequency REAL,
    label TEXT,
    bandwidth REAL,
    peak_power REAL,
    noise_floor REAL,
    snr REAL,
    device_id INTEGER,
    waterfall_data BLOB    -- Downsampled for visualization
);
```

## 🔧 Troubleshooting

### RTL-SDR Issues
```powershell
# Test RTL-SDR connection
python -c "from rtlsdr import RtlSdr; sdr = RtlSdr(); print(f'Device found: {sdr.get_device_serial_addresses()}')"

# Common fixes:
# 1. Install Zadig driver with WinUSB
# 2. Try different USB port
# 3. Check device manager for conflicts
# 4. Restart SDR# if running
```

### ML Training Issues
```powershell
# GPU memory issues
# Edit ml_training.py:
# GPU_MEMORY_LIMIT = 1024  # Reduce to 1GB

# TensorFlow issues
pip uninstall tensorflow tensorflow-gpu
pip install tensorflow==2.10.0

# Fallback to CPU-only
pip uninstall tensorflow-gpu
pip install tensorflow
```

### Database Issues
```powershell
# Reset databases
rm detections.db detections_ml.db
python init_db.py
python init_ml_db.py

# Check database integrity
python -c "import sqlite3; print(sqlite3.connect('detections.db').execute('SELECT COUNT(*) FROM detections').fetchone())"
```

### Performance Optimization
```powershell
# Reduce memory usage
# Edit listen.py: SCAN_STEP = 500000  # Larger steps
# Edit api.py: DEFAULT_PAGE_SIZE = 50  # Smaller pages

# Reduce chart data
# Waterfall charts automatically downsample for performance
```

## 📁 File Structure
```
rtl-classic/
├── listen.py              # Main signal detection (optimized output)
├── ml_listen.py          # ML-enhanced detection
├── api.py                # Flask web API (12+ chart types)
├── init_db.py            # Database initialization (optimized schema)
├── collect_baseline.py   # Legacy baseline collection
├── ml_data_collection.py # ML training data collection
├── ml_training.py        # ML model training (memory optimized)
├── scan.py               # Basic frequency scanner
├── requirements.txt      # Python dependencies 
├── templates/
│   └── dashboard.html    # Web dashboard (redesigned)
├── detections.db         # Main detection database
├── detections_ml.db      # ML detection database
├── baseline.json         # Legacy baseline data
├── training_data.json    # ML training dataset
├── *.pkl                 # Trained ML models
├── cnn_classifier.h5     # CNN model file
└── docs/
    ├── ML_SYSTEM_GUIDE.md
    ├── MEMORY_OPTIMIZATION.md
    ├── LISTEN_ENHANCEMENTS.md
    └── ML_SAVE_TROUBLESHOOTING.md
```

## 🎯 Usage Examples

### Monitor Specific Band
```powershell
# Edit listen.py frequency ranges for specific monitoring
# Example: Amateur radio 2m band only
FREQUENCY_RANGES = [(144e6, 148e6)]
python listen.py
```

### Export Detection Data
```powershell
# Get detections via API
curl "http://localhost:5000/detections?page_size=1000" > detections.json

# Or query database directly
python -c "
import sqlite3
import json
conn = sqlite3.connect('detections.db')
data = conn.execute('SELECT * FROM detections LIMIT 100').fetchall()
print(json.dumps(data, indent=2))
"
```

### Custom ML Training
```powershell
# Collect more training samples
# Edit ml_data_collection.py: num_samples_per_freq = 20
python ml_data_collection.py

# Train with custom parameters
# Edit ml_training.py CNN architecture or training epochs
python ml_training.py
```

## 🎉 Features Overview

### Console Output (Enhanced)
- **Compact display**: Single-line detection format
- **Confidence scoring**: ML-based confidence percentages  
- **Mini spectrum**: ASCII visualization of signal strength
- **Device info**: Real-time status and configuration
- **Color coding**: Signal types and quality indicators

### Web Dashboard (Redesigned)
- **Device selection**: Choose RTL-SDR device from table
- **Detection history**: Last 100 detections with filtering
- **Interactive charts**: Multiple visualization types
- **Responsive design**: Works on mobile and desktop
- **Real-time updates**: Automatic data refresh

### Data Storage (Optimized)
- **99% storage reduction**: From ~5MB to ~50KB per hour
- **Preserved visualization**: Waterfall data maintained
- **Essential metrics only**: Frequency, SNR, bandwidth, power
- **Downsampled FFT**: Compressed spectral data for charts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- RTL-SDR community for hardware support
- TensorFlow/Keras for ML framework
- Flask for web framework
- Chart.js for visualization library
- Tailwind CSS for responsive design
