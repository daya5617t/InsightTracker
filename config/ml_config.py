# ML Model Configuration for InsightTracker
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
MODELS_DIR = DATA_DIR / 'models'
DATASETS_DIR = DATA_DIR / 'datasets'

# Model paths
LSTM_MODEL_PATH = MODELS_DIR / 'lstm_model.h5'
WEIGHTS_PATH = MODELS_DIR / 'best_weights.weights.h5'

# Data paths
STOCK_DATA_PATH = DATASETS_DIR / 'all_stocks.csv'
HISTORICAL_DATA_DIR = DATASETS_DIR

# Model parameters
SEQUENCE_LENGTH = 60
PREDICTION_DAYS = 30
TRAIN_TEST_SPLIT = 0.8

# API Configuration
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
YAHOO_FINANCE_TIMEOUT = 30

# Cache settings
CACHE_TIMEOUT = 3600  # 1 hour
MAX_CACHE_SIZE = 1000

# Supported stock symbols
DEFAULT_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
    'META', 'NVDA', 'JPM', 'V', 'WMT'
]

# Market indices
INDICES = {
    'S&P 500': '^GSPC',
    'Dow Jones': '^DJI',
    'NASDAQ': '^IXIC',
    'Nikkei': '^N225',
    'FTSE 100': '^FTSE'
}

# Model hyperparameters
MODEL_CONFIG = {
    'lstm_units': [50, 50],
    'dropout_rate': 0.2,
    'learning_rate': 0.001,
    'batch_size': 32,
    'epochs': 100,
    'validation_split': 0.2,
    'patience': 10  # Early stopping patience
}

# Feature engineering
TECHNICAL_INDICATORS = [
    'SMA_10', 'SMA_20', 'SMA_50',
    'EMA_12', 'EMA_26',
    'RSI_14',
    'MACD',
    'BB_upper', 'BB_lower',
    'Volume_SMA_20'
]

# Data validation
MIN_DATA_POINTS = 100
MAX_MISSING_DATA_RATIO = 0.05

# Logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': ['file', 'console']
}