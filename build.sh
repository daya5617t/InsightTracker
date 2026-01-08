#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
# Collect static files
cd StockPricePrediction
python manage.py collectstatic --no-input

echo "Running migrations..."
# Run migrations
python manage.py migrate --no-input

echo "Build complete!"
