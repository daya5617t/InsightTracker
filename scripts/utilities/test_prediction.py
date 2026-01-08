import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockPricePrediction.settings')
django.setup()

from StockPricePredictionApp.ml_service import MLService

def test_prediction():
    ticker = 'AAPL'
    print(f"Testing prediction for {ticker}...")
    predictions = MLService.predict_stock_price(ticker, days=7)
    
    if predictions:
        print("Prediction successful!")
        for date, price in predictions:
            print(f"{date}: ${price:.2f}")
    else:
        print("Prediction failed.")

if __name__ == "__main__":
    test_prediction()
