#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install production server
pip install gunicorn whitenoise python-dotenv

# Collect static files
python StockPricePrediction/manage.py collectstatic --no-input

# Run migrations
python StockPricePrediction/manage.py migrate
