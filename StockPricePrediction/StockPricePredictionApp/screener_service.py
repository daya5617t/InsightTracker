"""
Stock Screener Service
Filter and screen stocks based on multiple criteria
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


class StockScreenerService:
    """Service for screening stocks based on criteria"""
    
    # Popular stock universes
    SP500_TICKERS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'XOM',
        'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'PEP',
        'COST', 'AVGO', 'KO', 'ADBE', 'WMT', 'MCD', 'CSCO', 'ACN', 'LIN', 'TMO',
        'NFLX', 'ABT', 'DHR', 'VZ', 'NKE', 'CRM', 'TXN', 'DIS', 'BMY', 'PM',
        'NEE', 'UPS', 'CMCSA', 'ORCL', 'INTC', 'AMD', 'HON', 'QCOM', 'RTX', 'IBM',
        # Add more as needed
    ]
    
    TECH_TICKERS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'ADBE', 'CRM',
        'ORCL', 'CSCO', 'INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'IBM', 'SNOW', 'PLTR',
        'SHOP', 'SQ', 'PYPL', 'UBER', 'ABNB', 'ROKU', 'ZM', 'DOCU', 'CRWD', 'NET'
    ]
    
    POPULAR_TICKERS = SP500_TICKERS[:50]  # Top 50 for performance
    
    @staticmethod
    def get_stock_data(ticker):
        """Fetch comprehensive stock data"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period='1y')
            
            if hist.empty:
                return None
            
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            if not current_price and not hist.empty:
                current_price = hist['Close'].iloc[-1]
            
            # Calculate metrics
            data = {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'current_price': round(current_price, 2),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0) or info.get('forwardPE', 0),
                'volume': info.get('volume', 0) or info.get('regularMarketVolume', 0),
                'avg_volume': info.get('averageVolume', 0) or info.get('averageVolume10days', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0),
                'eps': info.get('trailingEps', 0),
                'price_to_book': info.get('priceToBook', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'roe': info.get('returnOnEquity', 0),
                'profit_margin': info.get('profitMargins', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
            }
            
            # Calculate price changes
            if len(hist) > 0:
                data['day_change_percent'] = round(
                    ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) 
                    if len(hist) > 1 else 0, 2
                )
                data['week_change_percent'] = round(
                    ((hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5] * 100) 
                    if len(hist) > 5 else 0, 2
                )
                data['month_change_percent'] = round(
                    ((hist['Close'].iloc[-1] - hist['Close'].iloc[-21]) / hist['Close'].iloc[-21] * 100) 
                    if len(hist) > 21 else 0, 2
                )
                data['year_change_percent'] = round(
                    ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100) 
                    if len(hist) > 252 else 0, 2
                )
            else:
                data['day_change_percent'] = 0
                data['week_change_percent'] = 0
                data['month_change_percent'] = 0
                data['year_change_percent'] = 0
            
            return data
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    @staticmethod
    def screen_stocks(criteria, ticker_list=None, max_workers=10):
        """
        Screen stocks based on criteria
        
        Args:
            criteria: Dictionary of filter criteria
            ticker_list: List of tickers to screen (defaults to POPULAR_TICKERS)
            max_workers: Number of parallel threads for fetching data
        
        Returns:
            List of stocks matching criteria
        """
        if ticker_list is None:
            ticker_list = StockScreenerService.POPULAR_TICKERS
        
        # Fetch stock data in parallel
        stocks_data = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {
                executor.submit(StockScreenerService.get_stock_data, ticker): ticker 
                for ticker in ticker_list
            }
            
            for future in as_completed(future_to_ticker):
                data = future.result()
                if data:
                    stocks_data.append(data)
        
        # Apply filters
        filtered_stocks = []
        
        for stock in stocks_data:
            if StockScreenerService._matches_criteria(stock, criteria):
                filtered_stocks.append(stock)
        
        # Sort by specified field
        sort_by = criteria.get('sort_by', 'market_cap')
        reverse = criteria.get('sort_descending', True)
        
        try:
            filtered_stocks.sort(key=lambda x: x.get(sort_by, 0) or 0, reverse=reverse)
        except:
            pass
        
        return filtered_stocks
    
    @staticmethod
    def _matches_criteria(stock, criteria):
        """Check if stock matches filter criteria"""
        
        # Market Cap filter
        if 'min_market_cap' in criteria:
            if stock['market_cap'] < criteria['min_market_cap']:
                return False
        
        if 'max_market_cap' in criteria:
            if stock['market_cap'] > criteria['max_market_cap']:
                return False
        
        # P/E Ratio filter
        if 'min_pe_ratio' in criteria:
            if not stock['pe_ratio'] or stock['pe_ratio'] < criteria['min_pe_ratio']:
                return False
        
        if 'max_pe_ratio' in criteria:
            if not stock['pe_ratio'] or stock['pe_ratio'] > criteria['max_pe_ratio']:
                return False
        
        # Volume filter
        if 'min_volume' in criteria:
            if stock['volume'] < criteria['min_volume']:
                return False
        
        # Price filter
        if 'min_price' in criteria:
            if stock['current_price'] < criteria['min_price']:
                return False
        
        if 'max_price' in criteria:
            if stock['current_price'] > criteria['max_price']:
                return False
        
        # Dividend Yield filter
        if 'min_dividend_yield' in criteria:
            if not stock['dividend_yield'] or stock['dividend_yield'] < criteria['min_dividend_yield']:
                return False
        
        # Beta filter (volatility)
        if 'min_beta' in criteria:
            if not stock['beta'] or stock['beta'] < criteria['min_beta']:
                return False
        
        if 'max_beta' in criteria:
            if not stock['beta'] or stock['beta'] > criteria['max_beta']:
                return False
        
        # ROE filter
        if 'min_roe' in criteria:
            if not stock['roe'] or stock['roe'] < criteria['min_roe']:
                return False
        
        # Profit Margin filter
        if 'min_profit_margin' in criteria:
            if not stock['profit_margin'] or stock['profit_margin'] < criteria['min_profit_margin']:
                return False
        
        # Day/Week/Month/Year change filters
        if 'min_day_change' in criteria:
            if stock['day_change_percent'] < criteria['min_day_change']:
                return False
        
        if 'max_day_change' in criteria:
            if stock['day_change_percent'] > criteria['max_day_change']:
                return False
        
        if 'min_year_change' in criteria:
            if stock['year_change_percent'] < criteria['min_year_change']:
                return False
        
        # Sector filter
        if 'sectors' in criteria and criteria['sectors']:
            if stock['sector'] not in criteria['sectors']:
                return False
        
        return True
    
    @staticmethod
    def get_preset_screens():
        """Get predefined screening templates"""
        return {
            'growth_stocks': {
                'name': 'High Growth Stocks',
                'description': 'Stocks with high revenue and earnings growth',
                'criteria': {
                    'min_revenue_growth': 0.15,  # 15%
                    'min_earnings_growth': 0.15,
                    'min_market_cap': 1000000000,  # $1B
                    'sort_by': 'revenue_growth',
                    'sort_descending': True
                }
            },
            'value_stocks': {
                'name': 'Value Stocks',
                'description': 'Undervalued stocks with low P/E ratios',
                'criteria': {
                    'max_pe_ratio': 15,
                    'min_market_cap': 5000000000,  # $5B
                    'min_roe': 0.10,  # 10%
                    'sort_by': 'pe_ratio',
                    'sort_descending': False
                }
            },
            'dividend_stocks': {
                'name': 'Dividend Stocks',
                'description': 'High dividend yield stocks',
                'criteria': {
                    'min_dividend_yield': 0.03,  # 3%
                    'min_market_cap': 10000000000,  # $10B
                    'sort_by': 'dividend_yield',
                    'sort_descending': True
                }
            },
            'momentum_stocks': {
                'name': 'Momentum Stocks',
                'description': 'Stocks with strong upward price momentum',
                'criteria': {
                    'min_week_change': 5,  # 5% weekly gain
                    'min_month_change': 10,  # 10% monthly gain
                    'min_volume': 1000000,
                    'sort_by': 'month_change_percent',
                    'sort_descending': True
                }
            },
            'tech_leaders': {
                'name': 'Tech Leaders',
                'description': 'Leading technology companies',
                'criteria': {
                    'sectors': ['Technology'],
                    'min_market_cap': 50000000000,  # $50B
                    'min_profit_margin': 0.15,
                    'sort_by': 'market_cap',
                    'sort_descending': True
                }
            },
            'penny_stocks': {
                'name': 'Penny Stocks',
                'description': 'Low-priced high-risk stocks',
                'criteria': {
                    'max_price': 10,
                    'min_volume': 500000,
                    'sort_by': 'volume',
                    'sort_descending': True
                }
            }
        }
    
    @staticmethod
    def export_to_csv(stocks, filename='screener_results.csv'):
        """Export screening results to CSV"""
        if not stocks:
            return None
        
        df = pd.DataFrame(stocks)
        df.to_csv(filename, index=False)
        return filename
