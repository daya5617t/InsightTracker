import os
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib

# Constants
TICKER = 'AAPL'  # Train on a representative stock
START_DATE = '2015-01-01'
END_DATE = '2023-01-01'
PREDICTION_DAYS = 60
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'StockPricePredictionApp', 'ml_models', 'lstm_model.h5')
SCALER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'StockPricePredictionApp', 'ml_models', 'scaler.pkl')

def create_sequences(data, seq_length):
    X = []
    y = []
    for i in range(seq_length, len(data)):
        X.append(data[i-seq_length:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)

def train_model():
    print(f"Fetching data for {TICKER}...")
    data = yf.download(TICKER, start=START_DATE, end=END_DATE)
    
    if data.empty:
        print("Error: No data fetched.")
        return

    # Use 'Close' price
    dataset = data['Close'].values.reshape(-1, 1)

    # Scale data
    print("Scaling data...")
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset)

    # Create sequences
    print("Creating sequences...")
    X_train, y_train = create_sequences(scaled_data, PREDICTION_DAYS)
    
    # Reshape for LSTM [samples, time steps, features]
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # Build Model
    print("Building model...")
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train
    print("Training model (this may take a while)...")
    model.fit(X_train, y_train, epochs=5, batch_size=32) # Reduced epochs for quick setup

    # Save
    print(f"Saving model to {MODEL_PATH}...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save(MODEL_PATH)
    
    print(f"Saving scaler to {SCALER_PATH}...")
    joblib.dump(scaler, SCALER_PATH)
    
    print("Done!")

if __name__ == "__main__":
    train_model()
