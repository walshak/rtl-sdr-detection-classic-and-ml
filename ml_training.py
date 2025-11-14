"""
Train Isolation Forest and CNN models for anomaly detection and classification.
Expects training_data.json from ml_data_collection.py
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF warnings

import json
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from keras.layers import Input, Dense, Flatten, Conv1D, MaxPooling1D, Dropout
from keras.models import Sequential, Model
from keras.backend import clear_session
import matplotlib.pyplot as plt
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
            print(f"GPU memory limited to 2GB. {len(gpus)} GPU(s) detected.")
        except RuntimeError as e:
            print(f"GPU config error: {e}")
except Exception as e:
    print(f"GPU initialization note: {e}")

# Load training data
print("Loading training data...")
with open("training_data.json") as f:
    training_data = json.load(f)

print(f"Loaded {len(training_data)} samples")

# Extract features for Isolation Forest
features_list = ["peak_power", "noise_floor", "mean_power", "std_power", "min_power", "max_power", "snr", "kurtosis", "skewness", "bandwidth", "num_peaks"]
X_features = np.array([[d[f] for f in features_list] for d in training_data])

# Extract power spectra and raw samples for CNN
power_spectra = []
for d in training_data:
    arr = np.frombuffer(base64.b64decode(d["power_spectrum"]), dtype=np.float32)
    power_spectra.append(arr)

# Pad power spectra to same length
max_len = max(len(p) for p in power_spectra)
X_spectrum = np.array([np.pad(p, (0, max_len - len(p)), mode='constant') for p in power_spectra])

# Labels for CNN
label_to_idx = {label: idx for idx, label in enumerate(set(d["label"] for d in training_data))}
idx_to_label = {v: k for k, v in label_to_idx.items()}
y_labels = np.array([label_to_idx[d["label"]] for d in training_data])

print(f"Feature matrix shape: {X_features.shape}")
print(f"Spectrum matrix shape: {X_spectrum.shape}")
print(f"Labels: {idx_to_label}")

# ============ ISOLATION FOREST TRAINING ============
print("\n--- Training Isolation Forest ---")
scaler = StandardScaler()
X_features_scaled = scaler.fit_transform(X_features)

iso_forest = IsolationForest(contamination=0.1, random_state=42)
iso_forest.fit(X_features_scaled)

# Save scaler and model
with open("iso_forest_scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open("iso_forest_model.pkl", "wb") as f:
    pickle.dump(iso_forest, f)

print("Isolation Forest trained and saved.")

# ============ CNN TRAINING ============
print("\n--- Training CNN ---")

# Normalize spectrum
X_spectrum = (X_spectrum - np.mean(X_spectrum)) / (np.std(X_spectrum) + 1e-8)
X_spectrum = X_spectrum.reshape((X_spectrum.shape[0], X_spectrum.shape[1], 1))

# Build CNN with reduced complexity to save memory
model = Sequential([
    Conv1D(16, 3, activation='relu', input_shape=(max_len, 1)),
    MaxPooling1D(2),
    Conv1D(32, 3, activation='relu'),
    MaxPooling1D(2),
    Flatten(),
    Dense(32, activation='relu'),
    Dropout(0.3),
    Dense(len(label_to_idx), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print(model.summary())

# Train model with reduced batch size (4 instead of 8 to save memory)
history = model.fit(
    X_spectrum, y_labels,
    epochs=20,
    batch_size=4,
    validation_split=0.2,
    verbose=1
)

print("\nModel trained. Saving...")

# Save CNN model BEFORE clearing session
try:
    model.save("cnn_classifier.h5")
    print("✓ CNN model saved as cnn_classifier.h5")
except Exception as e:
    print(f"Warning: Error saving with .save(), trying alternative method: {e}")
    # Fallback: save weights and architecture separately
    import json
    model_json = model.to_json()
    with open("cnn_classifier_architecture.json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights("cnn_classifier_weights.h5")
    print("✓ CNN model saved as architecture (JSON) + weights (H5)")

with open("label_to_idx.pkl", "wb") as f:
    pickle.dump(label_to_idx, f)
print("✓ Label mappings saved as label_to_idx.pkl")

# Now clear session after saving
clear_session()

# Plot training history
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.title('Training Loss')

plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'], label='Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.title('Training Accuracy')
plt.tight_layout()
plt.savefig('training_history.png')
print("Training history saved to training_history.png")

print("\n--- Training Complete ---")
print(f"Models saved: iso_forest_model.pkl, iso_forest_scaler.pkl, cnn_classifier.h5, label_to_idx.pkl")
