import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

def initialize_stock_data():
    """Download and initialize stock data for the application"""
    print("Initializing stock data...")
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # List of S&P 500 companies for initial data
    try:
        print("Downloading S&P 500 companies list...")
        sp500_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        sp500_symbols = sp500_list['Symbol'].tolist()
        sp500_list.to_csv(os.path.join(data_dir, 'sp500_companies.csv'), index=False)
        print(f"Downloaded {len(sp500_symbols)} company symbols")
    except Exception as e:
        print(f"Error downloading S&P 500 list: {str(e)}")
        sp500_symbols = []

    # Download historical data for some major indices
    indices = {
        '^GSPC': 'S&P 500',
        '^DJI': 'Dow Jones',
        '^IXIC': 'NASDAQ',
        '^NYA': 'NYSE',
        '^FTSE': 'FTSE 100',
        '^N225': 'Nikkei 225'
    }
    
    print("\nDownloading major indices data...")
    for symbol, name in indices.items():
        try:
            print(f"Downloading {name} ({symbol}) data...")
            data = yf.download(symbol, start='2020-01-01', end=datetime.now().strftime('%Y-%m-%d'))
            data.to_csv(os.path.join(data_dir, f'{symbol.replace("^", "")}_historical.csv'))
            print(f"Successfully downloaded {name} data")
        except Exception as e:
            print(f"Error downloading {name} data: {str(e)}")

    # Download some sample stock data for popular companies
    sample_stocks = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
        'TSLA', 'NVDA', 'JPM', 'V', 'WMT'
    ]
    
    print("\nDownloading sample stock data...")
    all_stocks_data = []
    for symbol in sample_stocks:
        try:
            print(f"Downloading {symbol} data...")
            stock = yf.Ticker(symbol)
            hist = stock.history(period='1y')
            info = stock.info
            
            stock_data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'current_price': info.get('currentPrice', 0),
                'market_cap': info.get('marketCap', 0),
                'volume': info.get('volume', 0)
            }
            all_stocks_data.append(stock_data)
            
            # Save historical data
            hist.to_csv(os.path.join(data_dir, f'{symbol}_historical.csv'))
            print(f"Successfully downloaded {symbol} data")
        except Exception as e:
            print(f"Error downloading {symbol} data: {str(e)}")
    
    # Save all stocks summary data
    all_stocks_df = pd.DataFrame(all_stocks_data)
    all_stocks_df.to_csv(os.path.join(data_dir, 'all_stocks.csv'), index=False)
    
    print("\nData initialization complete!")
    return True

if __name__ == '__main__':
    initialize_stock_data()