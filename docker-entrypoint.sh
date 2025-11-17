#!/bin/bash
set -e

echo "🛰️  RTL-SDR Detection System - Docker Container"
echo "=============================================="

# Initialize database if it doesn't exist
if [ ! -f /app/data/detections.db ]; then
    echo "📦 Initializing database..."
    python init_db.py
fi

# Initialize ML database if it doesn't exist
if [ ! -f /app/data/ml_detections.db ]; then
    echo "🤖 Initializing ML database..."
    python init_ml_db.py
fi

# Check for RTL-SDR device
if lsusb | grep -i "Realtek.*RTL"; then
    echo "✅ RTL-SDR device detected"
else
    echo "⚠️  Warning: No RTL-SDR device detected"
    echo "   Container will start but SDR functions may not work"
fi

# Execute the main command
exec "$@"
