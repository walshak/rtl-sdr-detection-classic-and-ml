# ML-Based Signal Detection System

This system replaces static tolerance-based detection with machine learning:
- **Isolation Forest**: Detects anomalies (deviations from training baseline)
- **CNN**: Classifies signal types

## Full Data Collection & Training Pipeline

### Step 1: Install ML Dependencies
```powershell
pip install scikit-learn tensorflow matplotlib
```

### Step 2: Collect Training Data
Collect multiple samples per frequency to build a comprehensive baseline:
```powershell
python ml_data_collection.py
```

**What this does:**
- Collects 10 samples per frequency (configurable with `num_samples_per_freq` parameter)
- Saves to `training_data.json`
- Takes ~15-20 minutes for full spectrum

**Output:** `training_data.json` (~5-10 MB)

### Step 3: Train Models
Train Isolation Forest and CNN on collected data:
```powershell
python ml_training.py
```

**What this does:**
- **Isolation Forest**: Learns the normal feature space (peak power, SNR, bandwidth, etc.)
- **CNN**: Learns to classify power spectra by signal type
- Saves models:
  - `iso_forest_model.pkl` (anomaly detector)
  - `iso_forest_scaler.pkl` (feature scaler)
  - `cnn_classifier.h5` (signal classifier)
  - `label_to_idx.pkl` (label mappings)
- Generates `training_history.png` (training curves)

**Training time:** ~2-5 minutes

### Step 4: Initialize ML Detection Database
```powershell
python init_ml_db.py
```

**Creates:** `detections_ml.db` with schema for anomaly detections

### Step 5: Run ML-Based Listener
```powershell
python ml_listen.py
```

**What this does:**
- Continuously scans baseline frequencies
- **Isolation Forest** detects deviations from training baseline
- **CNN** classifies anomalies by signal type
- Saves detections to `detections_ml.db` with:
  - Anomaly score (True/False)
  - Predicted signal type
  - CNN confidence score

## How It Works

### Isolation Forest
- Learns the high-dimensional feature space from training data
- Detects signals that deviate significantly from normal patterns
- No manual tolerances needed—model learns what's "normal"

### CNN
- Learns to recognize signal types by power spectrum shape
- Used to classify anomalies (what type of new signal is it?)
- More robust to noise and variations than static classifiers

## Advantages Over Static Tolerances

| Aspect | Static Tolerances | ML-Based |
|--------|---|---|
| **Adaptation** | Fixed, rigid | Learns from data |
| **False Positives** | High (narrow tolerances) or High (wide tolerances) | Lower (data-driven) |
| **Frequency Scaling** | Manual tuning | Automatic |
| **New Signal Types** | Requires manual tolerance adjustment | Retrains on new data |
| **Classification** | Simple matching | Probabilistic confidence scores |

## Configuration

**ml_data_collection.py:**
- `num_samples_per_freq`: Number of samples per frequency (default: 10)
- `FREQUENCIES`: Which frequencies to scan

**ml_training.py:**
- `epochs`: CNN training epochs (default: 20)
- `contamination`: Isolation Forest anomaly rate (default: 0.1 = 10%)
- `batch_size`: CNN batch size (default: 8)

**ml_listen.py:**
- `DEVICE_LABEL`, `DEVICE_LAT`, `DEVICE_LONG`: Device metadata
- `SCAN_INTERVAL`: Seconds between scans (default: 10)

## Output Files

After training:
- `training_data.json`: Raw training samples
- `iso_forest_model.pkl`: Anomaly detector model
- `iso_forest_scaler.pkl`: Feature normalization
- `cnn_classifier.h5`: Signal type classifier
- `label_to_idx.pkl`: Signal type mappings
- `training_history.png`: Training plots
- `detections_ml.db`: Detected anomalies

## Retraining

To update models with new data:
1. Run `ml_data_collection.py` again
2. Run `ml_training.py` again
3. Restart `ml_listen.py`

## Next Steps

- API integration for ML detections
- Dashboard visualization of anomaly scores & confidence
- Incremental learning (update models without full retraining)
- Ensemble methods (combine Isolation Forest + CNN + statistical tests)
