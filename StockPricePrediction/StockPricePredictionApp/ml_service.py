import os
import numpy as np
import pandas as pd
import yfinance as yf
import joblib
from tensorflow.keras.models import load_model
from datetime import timedelta

# Paths
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml_models', 'lstm_model.h5')
SCALER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml_models', 'scaler.pkl')

class MLService:
    _model = None
    _scaler = None

    @classmethod
    def _load_artifacts(cls):
        if cls._model is None:
            if os.path.exists(MODEL_PATH):
                try:
                    cls._model = load_model(MODEL_PATH)
                    print("ML Model loaded successfully.")
                except Exception as e:
                    print(f"Error loading ML model: {e}")
            else:
                print(f"ML Model not found at {MODEL_PATH}")

        if cls._scaler is None:
            if os.path.exists(SCALER_PATH):
                try:
                    cls._scaler = joblib.load(SCALER_PATH)
                    print("Scaler loaded successfully.")
                except Exception as e:
                    print(f"Error loading scaler: {e}")
            else:
                print(f"Scaler not found at {SCALER_PATH}")

    @classmethod
    def predict_stock_price(cls, ticker, days=7):
        cls._load_artifacts()

        if cls._model is None or cls._scaler is None:
            print("Model or Scaler not available. Returning None.")
            return None

        try:
            # Fetch recent data with timeout (need at least 60 days for the sequence)
            print(f"Fetching data for {ticker}...")
            
            # Add timeout to prevent hanging - use threading
            import threading
            result_container = {'hist': None, 'error': None}
            
            def fetch_with_timeout():
                try:
                    stock = yf.Ticker(ticker)
                    result_container['hist'] = stock.history(period='6mo', interval='1d')
                except Exception as e:
                    result_container['error'] = e
            
            fetch_thread = threading.Thread(target=fetch_with_timeout)
            fetch_thread.daemon = True
            fetch_thread.start()
            fetch_thread.join(timeout=10)  # 10 second timeout
            
            if fetch_thread.is_alive():
                print(f"Timeout fetching data for {ticker} - falling back to heuristic")
                return None
            
            if result_container['error']:
                print(f"Error fetching data: {result_container['error']}")
                return None
                
            hist = result_container['hist']
            
            if hist is None or len(hist) < 60:
                print(f"Not enough history for {ticker}")
                return None

            # Use 'Close' price
            data = hist['Close'].values.reshape(-1, 1)
            
            # Scale data
            scaled_data = cls._scaler.transform(data)
            
            # Take the last 60 days
            current_batch = scaled_data[-60:].reshape(1, 60, 1)
            
            predicted_prices = []
            
            # Predict future days
            for i in range(days):
                # Get prediction (next day)
                next_prediction = cls._model.predict(current_batch, verbose=0)
                
                # Store prediction
                predicted_prices.append(next_prediction[0, 0])
                
                # Update batch: remove first day, add new prediction
                # next_prediction is (1, 1). We need (1, 1, 1) to append to (1, 59, 1)
                new_item = next_prediction.reshape(1, 1, 1)
                current_batch = np.append(current_batch[:, 1:, :], new_item, axis=1)
            
            # Inverse transform predictions
            predicted_prices = np.array(predicted_prices).reshape(-1, 1)
            predicted_prices = cls._scaler.inverse_transform(predicted_prices)
            
            # Generate dates
            last_date = hist.index[-1]
            if hasattr(last_date, 'tz_localize'):
                 last_date = last_date.tz_localize(None)
            elif hasattr(last_date, 'tz'):
                 last_date = last_date.replace(tzinfo=None)
                 
            future_dates = []
            current_date = last_date
            for i in range(days):
                current_date += timedelta(days=1)
                # Skip weekends if desired, but for simplicity we'll just add days
                # while current_date.weekday() >= 5:
                #     current_date += timedelta(days=1)
                future_dates.append(current_date.strftime('%Y-%m-%d'))
            
            return [(date, float(price)) for date, price in zip(future_dates, predicted_prices.flatten())]

        except Exception as e:
            print(f"Prediction error for {ticker}: {e}")
            return None
