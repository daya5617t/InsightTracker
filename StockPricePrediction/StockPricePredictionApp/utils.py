import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from .models import Stock, StockPrice, MarketIndex

def initialize_stock_data():
    """Initialize stock data from major indices"""
    # List of major companies to track
    symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'JPM', 'V', 'WMT',
        'PG', 'JNJ', 'XOM', 'BAC', 'MA', 'UNH', 'HD', 'CVX', 'KO', 'PFE'
    ]  # Top 20 commonly traded stocks
    
    for symbol in symbols:
        try:
            # Get stock info
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Create or update stock record
            stock_obj, created = Stock.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': info.get('longName', info.get('shortName', symbol)),
                    'current_price': info.get('regularMarketPrice', 0),
                    'change_percent': info.get('regularMarketChangePercent', 0),
                    'volume': info.get('regularMarketVolume', 0),
                    'market_cap': info.get('marketCap', 0)
                }
            )
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            hist = stock.history(start=start_date, end=end_date)
            
            # Save historical prices
            for date, row in hist.iterrows():
                StockPrice.objects.update_or_create(
                    stock=stock_obj,
                    date=date,
                    defaults={
                        'open_price': row['Open'],
                        'high_price': row['High'],
                        'low_price': row['Low'],
                        'close_price': row['Close'],
                        'volume': row['Volume']
                    }
                )
                
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            continue

def initialize_market_indices():
    """Initialize market indices data"""
    indices = {
        '^GSPC': 'S&P 500',
        '^DJI': 'Dow Jones Industrial Average',
        '^IXIC': 'NASDAQ Composite',
        '^NYA': 'NYSE Composite',
        '^FTSE': 'FTSE 100',
        '^N225': 'Nikkei 225',
        '000001.SS': 'Shanghai Composite',
        '^HSI': 'Hang Seng'
    }
    
    for symbol, name in indices.items():
        try:
            # Get index data
            index = yf.Ticker(symbol)
            info = index.info
            
            MarketIndex.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': name,
                    'current_value': info.get('regularMarketPrice', 0),
                    'change_percent': info.get('regularMarketChangePercent', 0)
                }
            )
            
        except Exception as e:
            print(f"Error processing index {symbol}: {str(e)}")
            continue

def update_all_data():
    """Update all stock and index data"""
    initialize_stock_data()
    initialize_market_indices()