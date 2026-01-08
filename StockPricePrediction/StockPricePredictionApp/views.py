import re
import csv
import yfinance as yf
import math
from .ml_service import MLService
import pandas as pd
import numpy as np
from datetime import timedelta, date
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Watchlist
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import os
import requests
from datetime import datetime, timedelta
import feedparser
import json
from collections import OrderedDict
from .sample_data import (
    get_sample_news,
    get_sample_stock_history,
    get_sample_browse_stocks,
    get_default_sample_symbols,
)
try:
    import pytz
except ImportError:
    pytz = None


df = None
df1 = None
df2 = None

# Small lat/lon lookup for common countries
_COUNTRY_COORDS = {
    "United States": {"lat": 37.0902, "lon": -95.7129},
    "India": {"lat": 20.5937, "lon": 78.9629},
    "China": {"lat": 35.8617, "lon": 104.1954},
    "Japan": {"lat": 36.2048, "lon": 138.2529},
    "United Kingdom": {"lat": 55.3781, "lon": -3.4360},
    "Canada": {"lat": 56.1304, "lon": -106.3468},
    "Australia": {"lat": -25.2744, "lon": 133.7751},
    "Germany": {"lat": 51.1657, "lon": 10.4515},
    "France": {"lat": 46.2276, "lon": 2.2137},
    "Brazil": {"lat": -14.2350, "lon": -51.9253},
    "South Korea": {"lat": 35.9078, "lon": 127.7669},
    "Netherlands": {"lat": 52.1326, "lon": 5.2913},
    "Switzerland": {"lat": 46.8182, "lon": 8.2275},
    "Taiwan": {"lat": 23.6978, "lon": 120.9605},
    "Spain": {"lat": 40.4637, "lon": -3.7492},
    "Mexico": {"lat": 23.6345, "lon": -102.5528},
    "Italy": {"lat": 41.8719, "lon": 12.5674},
    "Sweden": {"lat": 60.1282, "lon": 18.6435},
    "Norway": {"lat": 60.4720, "lon": 8.4689},
    "Argentina": {"lat": -38.4161, "lon": -63.6167},
    "South Africa": {"lat": -30.5595, "lon": 22.9375},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694},
    "Singapore": {"lat": 1.3521, "lon": 103.8198},
    "Denmark": {"lat": 56.2639, "lon": 9.5018},
}


def get_all_available_stocks():
    """Returns a dict of all available stock tickers mapped to countries - CACHED"""
    cache_key = 'all_available_stocks_dict_v2'
    stocks = cache.get(cache_key)
    if stocks:
        return stocks
    
    stocks = {
        # United States (NYSE/NASDAQ)
        "AAPL": "United States", "TSLA": "United States", "MSFT": "United States", "GOOGL": "United States",
        "AMZN": "United States", "META": "United States", "NVDA": "United States", "NFLX": "United States",
        "JPM": "United States", "BAC": "United States", "WFC": "United States", "JNJ": "United States",
        "PFE": "United States", "UNH": "United States", "V": "United States", "MA": "United States",
        "DIS": "United States", "NKE": "United States", "WMT": "United States", "HD": "United States",
        "PG": "United States", "KO": "United States", "PEP": "United States", "MCD": "United States",

        # United Kingdom (LSE)
        "UL": "United Kingdom", "BP": "United Kingdom", "HSBC": "United Kingdom", "GSK": "United Kingdom",
        "AZN": "United Kingdom", "RIO.L": "United Kingdom", "VOD": "United Kingdom",
        "BT": "United Kingdom", "BA": "United Kingdom", "LLOY": "United Kingdom", "RDS-A": "United Kingdom",

        # Canada (TSX)
        "RY": "Canada", "TD": "Canada", "BNS": "Canada", "CNR": "Canada", "CP": "Canada",
        "SHOP": "Canada", "SU": "Canada", "TRP": "Canada", "ENB": "Canada", "BMO": "Canada",

        # Australia (ASX)
        "BHP": "Australia", "RIO": "Australia", "CBA": "Australia", "ANZ": "Australia",
        "WBC": "Australia", "NAB": "Australia", "TLS": "Australia", "WOW": "Australia",
        "WDS": "Australia", "FMG": "Australia", "CSL": "Australia", "TCL": "Australia",

        # Japan (TSE)
        "TM": "Japan", "SONY": "Japan", "7203.T": "Japan", "6758.T": "Japan", "9984.T": "Japan",
        "8306.T": "Japan", "9434.T": "Japan", "8058.T": "Japan", "7267.T": "Japan", "4503.T": "Japan",
        "6098.T": "Japan", "8031.T": "Japan", "4063.T": "Japan", "4502.T": "Japan",

        # China (SSE/SZSE)
        "BABA": "China", "TCEHY": "China", "JD": "China", "PDD": "China", "NIO": "China",
        "XPEV": "China", "LI": "China", "BIDU": "China", "NTES": "China", "WB": "China",
        "BILI": "China", "TME": "China", "VIPS": "China", "YMM": "China",

        # India (NSE/BSE)
        "RELIANCE.NS": "India", "TCS.NS": "India", "INFY.NS": "India", "HDFCBANK.NS": "India",
        "ICICIBANK.NS": "India", "LT.NS": "India", "SBIN.NS": "India", "ITC.NS": "India",
        "BAJFINANCE.NS": "India", "ASIANPAINT.NS": "India", "HINDUNILVR.NS": "India",
        "ADANIENT.NS": "India", "TITAN.NS": "India", "SUNPHARMA.NS": "India", "BHARTIARTL.NS": "India",
        "KOTAKBANK.NS": "India", "AXISBANK.NS": "India", "MARUTI.NS": "India", "NESTLEIND.NS": "India",

        # Additional countries...
        "SAP": "Germany", "SAP.DE": "Germany", "SIE.DE": "Germany", "BMW.DE": "Germany",
        "TTE": "France", "MC.PA": "France", "OR.PA": "France", "BNP.PA": "France",
        "ASML": "Netherlands", "ING": "Netherlands", "NVS": "Switzerland", "ROG.SW": "Switzerland",
        "TSM": "Taiwan", "2330.TW": "Taiwan", "VALE": "Brazil", "PBR": "Brazil",
        "AMX": "Mexico", "GGAL": "Argentina", "NPN.JO": "South Africa",
    }
    cache.set(cache_key, stocks, timeout=3600)  # Cache for 1 hour
    return stocks


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def load_stock_dataset(symbol, start=None, end=None, period='6mo', interval='1d', force_sample=False):
    """Fetch OHLCV data for a symbol with sample-data fallback."""
    symbol = (symbol or '').strip()
    if not symbol:
        return None

    requested_symbol = symbol.upper()
    data_symbol = requested_symbol
    used_sample = False
    hist = None
    ticker_for_info = None

    if not force_sample:
        try:
            ticker_for_info = yf.Ticker(symbol)
            if start is not None or end is not None:
                hist = ticker_for_info.history(start=start, end=end, interval=interval)
            else:
                hist = ticker_for_info.history(period=period, interval=interval)
        except Exception as fetch_err:
            print(f"History fetch error for {symbol}: {fetch_err}")
            hist = None

    if hist is None or hist.empty or 'Close' not in getattr(hist, 'columns', []):
        sample_history = get_sample_stock_history(symbol)
        fallback_symbol = None
        if sample_history is None:
            fallback_symbol = get_default_sample_symbols()[0]
            sample_history = get_sample_stock_history(fallback_symbol)
        if sample_history:
            used_sample = True
            data_symbol = (fallback_symbol or requested_symbol).upper()
            hist = pd.DataFrame(sample_history)
            hist['Date'] = pd.to_datetime(hist['Date'])
            hist = hist.set_index('Date')
            try:
                ticker_for_info = yf.Ticker(fallback_symbol or symbol)
            except Exception:
                ticker_for_info = None
        else:
            return None

    if isinstance(hist.columns, pd.MultiIndex):
        hist.columns = [col[0] if isinstance(col, tuple) else col for col in hist.columns]

    rename_map = {}
    cols_lower = {str(c).lower(): c for c in hist.columns}
    for want in ['open', 'high', 'low', 'close', 'volume']:
        if want in cols_lower:
            rename_map[cols_lower[want]] = want.title()
    if rename_map:
        hist = hist.rename(columns=rename_map)

    if 'Close' not in hist.columns:
        for col in hist.columns:
            if 'close' in str(col).lower():
                hist['Close'] = hist[col]
                break

    if 'Close' not in hist.columns:
        return None

    hist = hist.dropna(subset=['Close'])
    if hist.empty:
        return None

    index = hist.index
    if hasattr(index, 'tz_localize'):
        try:
            index = index.tz_localize(None)
        except Exception:
            index = index.tz_convert(None)

    x = pd.Index(index).strftime('%Y-%m-%d').tolist()

    close_s = hist['Close'].astype(float).round(2)
    open_s = hist['Open'].astype(float).round(2) if 'Open' in hist.columns else close_s
    high_s = hist['High'].astype(float).round(2) if 'High' in hist.columns else close_s
    low_s = hist['Low'].astype(float).round(2) if 'Low' in hist.columns else close_s

    if 'Volume' in hist.columns:
        volume_s = hist['Volume'].fillna(0).astype('int64')
    else:
        volume_s = pd.Series([0] * len(close_s), index=hist.index, dtype='int64')

    y_open = [float(val) for val in open_s.to_list()]
    y_close = [float(val) for val in close_s.to_list()]
    y_high = [float(val) for val in high_s.to_list()]
    y_low = [float(val) for val in low_s.to_list()]
    y_volume = [int(float(val)) if pd.notna(val) and float(val) >= 0 else 0 for val in volume_s.to_list()]

    first_close = float(y_close[0])
    last_close = float(y_close[-1])
    
    # Always try to fetch current live price
    current_live_price = None
    try:
        live_ticker = yf.Ticker(requested_symbol)
        live_info = live_ticker.fast_info
        current_live_price = live_info.last_price
        if current_live_price and current_live_price > 0:
            last_close = round(float(current_live_price), 2)
    except Exception as e:
        print(f"Could not fetch live price for {requested_symbol}: {e}")
    
    change_price = round(last_close - first_close, 2)
    change_pct = round((change_price / first_close) * 100, 2) if first_close else 0.0

    min_price = round(min(y_low), 2) if y_low else last_close
    max_price = round(max(y_high), 2) if y_high else last_close

    df_data = pd.DataFrame({
        'Open': y_open,
        'High': y_high,
        'Low': y_low,
        'Close': y_close,
        'Volume': y_volume,
        'Date': x
    })

    description_info = OrderedDict()
    info = {}
    if ticker_for_info is None:
        try:
            ticker_for_info = yf.Ticker(data_symbol)
        except Exception:
            ticker_for_info = None
    if ticker_for_info is not None:
        try:
            info = ticker_for_info.info or {}
        except Exception:
            info = {}

    market_cap_value = info.get('marketCap')
    if isinstance(market_cap_value, (int, float)) and market_cap_value:
        market_cap_str = f"${market_cap_value:,.0f}"
    else:
        market_cap_str = 'N/A'

    description_info['Company Name'] = info.get('longName') or info.get('shortName') or data_symbol
    description_info['Sector'] = info.get('sector') or 'N/A'
    description_info['Industry'] = info.get('industry') or 'N/A'
    description_info['Country'] = info.get('country') or 'N/A'
    description_info['Website'] = info.get('website') or 'N/A'
    description_info['Market Cap'] = market_cap_str
    description_info['Summary'] = info.get('longBusinessSummary') or 'Not available.'

    return {
        'requested_symbol': requested_symbol,
        'data_symbol': data_symbol,
        'used_sample': used_sample,
        'current_live_price': current_live_price,
        'x': x,
        'y_open': y_open,
        'y_close': y_close,
        'y_high': y_high,
        'y_low': y_low,
        'y_volume': y_volume,
        'last_day_price': round(last_close, 2),
        'min_price': min_price,
        'max_price': max_price,
        'change_in_price': change_price,
        'change_in_precentage': change_pct,
        'df': df_data,
        'df_values': [
            (row['Open'], row['High'], row['Low'], row['Close'], row['Volume'], row['Date'])
            for _, row in df_data.iterrows()
        ],
        'description': description_info,
    }


# ------------------------------------------------------------------
# News Feed Views
# ------------------------------------------------------------------
def news_feed(request):
    """Renders the news feed page with fetched news data"""
    cache_key = 'market_news'
    cached_news = cache.get(cache_key)

    if cached_news:
        news_items = cached_news
    else:
        news_items = []
        try:
            feed_url = 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US'
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:20]:  # Get up to 20 news items
                # Extract related ticker from title or summary
                related_ticker = None
                title_lower = entry.title.lower()
                summary_lower = entry.summary.lower() if hasattr(entry, 'summary') else ''

                # Look for common stock tickers in the text
                common_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN',
                                  'TSLA', 'META', 'NVDA', 'SPY', 'QQQ', 'DIA']
                for ticker in common_tickers:
                    if ticker.lower() in title_lower or ticker.lower() in summary_lower:
                        related_ticker = ticker
                        break

                # Parse published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_date = datetime(*entry.published_parsed[:6])
                    except:
                        published_date = datetime.now()

                # Extract publisher/source
                publisher = 'Yahoo Finance'
                if hasattr(entry, 'source') and entry.source:
                    publisher = entry.source
                elif hasattr(entry, 'author') and entry.author:
                    publisher = entry.author

                news_items.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else '',
                    'published_date': published_date,
                    'summary': entry.summary if hasattr(entry, 'summary') else '',
                    'source': 'Yahoo Finance',
                    'publisher': publisher,
                    'related_ticker': related_ticker
                })

            # Cache for 15 minutes
            cache.set(cache_key, news_items, timeout=900)
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            # Return empty list if fetch fails
            news_items = []

    if not news_items:
        news_items = get_sample_news()
        messages.info(
            request, 'Live news is unavailable. Displaying sample headlines.')
        cache.set(cache_key, news_items, timeout=300)

    context = {
        'news_items': news_items,
        'total_news': len(news_items),
        'last_updated': datetime.now()
    }

    return render(request, 'news_feed.html', context)


def news_api(request):
    """API endpoint for fetching stock market news"""
    cache_key = 'market_news'
    cached_news = cache.get(cache_key)

    if cached_news:
        return JsonResponse({'news': cached_news})

    try:
        feed_url = 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US'
        feed = feedparser.parse(feed_url)

        news_items = []
        for entry in feed.entries[:10]:
            news_items.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                'summary': entry.summary
            })

        if news_items:
            cache.set(cache_key, news_items, timeout=900)
            return JsonResponse({'news': news_items})
    except Exception as e:
        print(f"News API error: {e}")

    # Fallback to sample news
    sample_news = get_sample_news()
    cache.set(cache_key, sample_news, timeout=300)
    return JsonResponse({'news': sample_news, 'fallback': True})


# Analytics Views
def analytics_map(request):
    """Renders the analytics map page with computed data.

    Builds a lightweight summary so the page shows non-empty visuals without
    hammering external APIs. Data is cached for a short period.
    """
    try:
        cache_key = 'analytics_map_context_v1'
        cached = cache.get(cache_key)
        if cached:
            return render(request, 'template/analytics_map.html', cached)

        stocks_map = get_all_available_stocks()
        available_stocks = [(ticker, country)
                            for ticker, country in stocks_map.items()]

        # Group symbols by country
        country_symbols = {}
        for sym, ctry in stocks_map.items():
            country_symbols.setdefault(ctry, []).append(sym)

        # Helper to safely collect a small summary for a symbol (with caching)
        def fetch_summary(symbol, country):
            import math
            # Check cache first (15 minute cache)
            cache_key_symbol = f'stock_summary_{symbol}'
            cached_data = cache.get(cache_key_symbol)
            if cached_data:
                return cached_data

            name = symbol
            sector = 'N/A'
            price = 0.0
            market_cap = 0
            change_30d = 0.0
            try:
                t = yf.Ticker(symbol)
                # Use history first to get both price and change in one call (more efficient)
                try:
                    hist = t.history(period='1mo', interval='1d')
                    if not hist.empty and len(hist) >= 2 and 'Close' in hist.columns:
                        last = float(hist['Close'].iloc[-1])
                        first = float(hist['Close'].iloc[0])
                        price = last
                        if first and first != 0:
                            change_30d = round((last - first) / first * 100, 2)
                except Exception:
                    pass
                # Fallback to fast_info if history didn't work
                if not price:
                    try:
                        fi = t.fast_info
                        price = float(fi.get('lastPrice') or fi.get(
                            'regularMarketPrice') or 0)  # type: ignore
                    except Exception:
                        pass
                # Get company info (cache this separately if needed)
                try:
                    info = t.info
                    name = info.get('shortName') or info.get(
                        'longName') or symbol
                    sector = info.get('sector') or 'N/A'
                    market_cap = int(info.get('marketCap') or 0)
                    if not price:
                        price = float(info.get('currentPrice')
                                      or info.get('regularMarketPrice') or 0)
                except Exception:
                    pass
            except Exception:
                pass
            # Sanitize numbers for JSON safety
            if not isinstance(price, (int, float)) or math.isnan(price) or math.isinf(price):
                price = 0.0
            if not isinstance(change_30d, (int, float)) or math.isnan(change_30d) or math.isinf(change_30d):
                change_30d = 0.0
            try:
                market_cap = int(market_cap or 0)
            except Exception:
                market_cap = 0

            result = {
                'symbol': symbol,
                'name': name,
                'country': country,
                'price': float(price),
                'change_30d': float(change_30d),
                'sector': sector,
                'market_cap': market_cap,
            }
            # Cache for 15 minutes
            cache.set(cache_key_symbol, result, timeout=900)
            return result

        # Build per-country aggregates using a small sample for performance
        geographic_data = []
        stock_details = []
        
        # Add timeout to prevent hanging
        import signal
        from contextlib import contextmanager
        
        @contextmanager
        def timeout_context(seconds):
            def timeout_handler(signum, frame):
                raise TimeoutError()
            old_handler = signal.signal(signal.SIGALRM, timeout_handler) if hasattr(signal, 'SIGALRM') else None
            if hasattr(signal, 'alarm'):
                signal.alarm(seconds)
            try:
                yield
            finally:
                if hasattr(signal, 'alarm'):
                    signal.alarm(0)
                if old_handler and hasattr(signal, 'SIGALRM'):
                    signal.signal(signal.SIGALRM, old_handler)
        
        for country, symbols in country_symbols.items():
            sample = symbols[:3]  # keep it small/fast
            samples_details = []
            
            # Try to fetch data with timeout
            for sym in sample:
                try:
                    # Skip if taking too long (use cached or skip)
                    d = fetch_summary(sym, country)
                    stock_details.append(d)
                    samples_details.append(d)
                except Exception as e:
                    print(f"Skipping {sym} due to error: {e}")
                    continue
            
            # Always add country data even if we couldn't fetch stock details
            if samples_details:
                avg_perf = round(np.mean(
                    [s['change_30d'] for s in samples_details if s is not None]), 2) if samples_details else 0.0
                total_mc = int(
                    sum([int(s.get('market_cap', 0) or 0) for s in samples_details]))
            else:
                avg_perf = 0.0
                total_mc = 0
            
            geographic_data.append({
                'country': country,
                'stocks_count': len(symbols),
                'avg_performance': avg_perf,
                'total_market_cap': total_mc,
                'stocks': ", ".join(sample)
            })

        # Build a correlation network across a subset of stocks (optimized for performance)
        # Check cache first for correlation data
        cache_key_corr = 'correlation_data_analytics'
        correlation_data = cache.get(cache_key_corr)
        if correlation_data is None:
            correlation_data = []
            try:
                selected = [d['symbol'] for d in stock_details][:10]
                price_frames = []
                for sym in selected:
                    try:
                        t = yf.Ticker(sym)
                        hist = t.history(period='1mo', interval='1d')
                        if not hist.empty and 'Close' in hist.columns:
                            price_frames.append(hist['Close'].rename(sym))
                    except Exception:
                        continue
                if price_frames and len(price_frames) >= 2:
                    prices = pd.concat(price_frames, axis=1)
                    if prices.shape[1] >= 2:
                        rets = prices.pct_change()
                        corr = rets.corr(min_periods=5)
                        syms = list(corr.columns)
                        edges = []
                        for i in range(len(syms)):
                            for j in range(i + 1, len(syms)):
                                val = corr.iloc[i, j]
                                if pd.notna(val):
                                    edges.append(
                                        (syms[i], syms[j], float(val)))
                        strong = [(a, b, v)
                                  for (a, b, v) in edges if abs(v) >= 0.3]
                        chosen = strong if strong else sorted(
                            edges, key=lambda t: -abs(t[2]))[:10]
                        for a, b, v in chosen:
                            correlation_data.append({
                                'source': a,
                                'target': b,
                                'value': round(abs(float(v)), 2)
                            })
            except Exception as e:
                print(f"Correlation data error: {e}")
            cache.set(cache_key_corr, correlation_data, timeout=1800)

        # Last-resort fallback: create a minimal chain so the UI has something to render
        if not correlation_data and stock_details and len(stock_details) >= 2:
            chain = [d['symbol'] for d in stock_details[:10]]
            for a, b in zip(chain, chain[1:]):
                correlation_data.append(
                    {'source': a, 'target': b, 'value': 0.2})

        total_stocks = len(stocks_map)
        total_countries = len(country_symbols)

        # Segment stock cards for UI sections
        asian_countries = {'India', 'Japan', 'China',
                           'Taiwan', 'South Korea', 'Hong Kong', 'Singapore'}
        indian_stocks = [d for d in stock_details if d['country'] == 'India']
        other_asian_stocks = [d for d in stock_details if d['country']
                              in asian_countries and d['country'] != 'India']
        other_stocks = [
            d for d in stock_details if d['country'] not in asian_countries]

        # Convert data to JSON for JavaScript
        import json
        context = {
            'available_stocks': available_stocks,
            'total_stocks': total_stocks,
            'total_countries': total_countries,
            'geographic_data': json.dumps(geographic_data),
            'stock_details': json.dumps(stock_details),
            'correlation_data': json.dumps(correlation_data),
            'indian_stocks': indian_stocks,
            'other_asian_stocks': other_asian_stocks,
            'other_stocks': other_stocks,
        }
        
        # Cache for 1 hour (3600 seconds) so analytics persists
        cache.set(cache_key, context, timeout=3600)
        
        return render(request, 'template/analytics_map.html', context)
    except Exception as e:
        # Fail safe – render the page with minimal context
        import traceback
        print("=" * 80)
        print("ANALYTICS MAP ERROR:")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
        print("=" * 80)
        
        stocks_dict = get_all_available_stocks()
        available_stocks = [(ticker, country)
                            for ticker, country in stocks_dict.items()]
        
        import json
        return render(request, 'template/analytics_map.html', {
            'available_stocks': available_stocks,
            'total_stocks': len(stocks_dict),
            'total_countries': len(set(stocks_dict.values())),
            'geographic_data': json.dumps([]),
            'stock_details': json.dumps([]),
            'correlation_data': json.dumps([]),
            'correlation_data': [],
            'indian_stocks': [],
            'other_asian_stocks': [],
            'other_stocks': [],
        })


@require_GET
def analytics_map_api(request):
    """Returns aggregated data for the analytics map"""
    cache_key = 'analytics_map_summary'
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse(cached)

    try:
        stocks_map = get_all_available_stocks()
        country_counts = {}
        for ticker, country in stocks_map.items():
            country_counts[country] = country_counts.get(country, 0) + 1

        geo_data = []
        for country, count in country_counts.items():
            coords = _COUNTRY_COORDS.get(country, None)
            geo_data.append({
                "country": country,
                "count": count,
                "lat": coords['lat'] if coords else None,
                "lon": coords['lon'] if coords else None
            })

        payload = {
            "total_stocks": sum(country_counts.values()),
            "countries": len(country_counts),
            "regions": 0,
            "connections": 0,
            "geo_data": geo_data
        }

        cache.set(cache_key, payload, timeout=600)
        return JsonResponse(payload)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def market_overview_api(request):
    """API endpoint for market overview data (cached for 5 minutes)"""
    cache_key = 'market_overview_data'
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data)

    try:
        t = yf.Ticker('^GSPC')
        sp500 = t.history(period='1mo', interval='1d')

        if sp500.empty or 'Close' not in sp500.columns:
            return JsonResponse({'error': 'No data available'}, status=500)

        data = {
            'labels': sp500.index.strftime('%Y-%m-%d').tolist(),
            'values': sp500['Close'].round(2).tolist(),
            'stats': {
                'marketCap': calculate_market_cap(),
                'volume': int(sp500['Volume'].iloc[-1]) if 'Volume' in sp500.columns else 0,
                'advancing': count_advancing_stocks(),
                'declining': count_declining_stocks()
            }
        }

        # Cache for 5 minutes
        cache.set(cache_key, data, timeout=300)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def market_overview_timeframe_api(request, timeframe):
    """API endpoint for market overview data with different timeframes (cached for 5 minutes)"""
    cache_key = f'market_overview_{timeframe}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data)

    try:
        timeframe_map = {
            '1d': '1d',
            '1w': '5d',
            '1m': '1mo',
            '3m': '3mo',
            '1y': '1y'
        }

        period = timeframe_map.get(timeframe, '1mo')
        interval = '1d' if timeframe != '1d' else '5m'

        t = yf.Ticker('^GSPC')
        sp500 = t.history(period=period, interval=interval)

        if sp500.empty or 'Close' not in sp500.columns:
            return JsonResponse({'error': 'No data available'}, status=500)

        data = {
            'labels': sp500.index.strftime('%Y-%m-%d %H:%M' if interval == '5m' else '%Y-%m-%d').tolist(),
            'values': sp500['Close'].round(2).tolist()
        }

        # Cache for 5 minutes
        cache.set(cache_key, data, timeout=300)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def global_markets_api(request):
    """API endpoint for global market data (cached for 5 minutes)"""
    cache_key = 'global_markets_data'
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data)

    try:
        indices = {
            'NYA': '^NYA',
            'IXIC': '^IXIC',
            'FTSE': '^FTSE',
            'N225': '^N225',
            'SSEC': '000001.SS',
            'HSI': '^HSI',
            'DAX': '^GDAXI',
            'SENSEX': '^BSESN'
        }

        markets_data = {}
        for market, symbol in indices.items():
            try:
                t = yf.Ticker(symbol)
                data = t.history(period='2d', interval='1d')
                if not data.empty and len(data) >= 2 and 'Close' in data.columns:
                    prev_close = float(data['Close'].iloc[-2])
                    current = float(data['Close'].iloc[-1])
                    if prev_close and prev_close != 0:
                        change = ((current - prev_close) / prev_close) * 100
                    else:
                        change = 0.0

                    markets_data[market] = {
                        'index': round(current, 2),
                        'change': round(change, 2),
                        'volume': int(data['Volume'].iloc[-1]) if 'Volume' in data.columns else 0
                    }
            except Exception as e:
                print(f"Error fetching data for {market}: {str(e)}")
                continue

        response_data = {'markets': markets_data}
        # Cache for 5 minutes
        cache.set(cache_key, response_data, timeout=300)
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Helper Functions
def calculate_market_cap():
    """Calculate total market cap of major indices"""
    try:
        indices = ['^GSPC', '^DJI', '^IXIC']
        total_market_cap = 0

        for index in indices:
            ticker = yf.Ticker(index)
            info = ticker.info
            if 'marketCap' in info:
                total_market_cap += info['marketCap']

        return total_market_cap
    except:
        return 0


def count_advancing_stocks():
    """Count number of advancing stocks in S&P 500"""
    try:
        sp500_list = pd.read_html(
            'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        symbols = sp500_list['Symbol'].tolist()

        advancing = 0
        for symbol in symbols[:50]:
            try:
                stock = yf.download(symbol, period='2d', progress=False)
                if stock['Close'].iloc[-1] > stock['Close'].iloc[-2]:
                    advancing += 1
            except:
                continue

        return int(advancing * (500/50))
    except:
        return 0


def count_declining_stocks():
    """Count number of declining stocks in S&P 500"""
    try:
        sp500_list = pd.read_html(
            'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        symbols = sp500_list['Symbol'].tolist()

        declining = 0
        for symbol in symbols[:50]:
            try:
                stock = yf.download(symbol, period='2d', progress=False)
                if stock['Close'].iloc[-1] < stock['Close'].iloc[-2]:
                    declining += 1
            except:
                continue

        return int(declining * (500/50))
    except:
        return 0


# Main Views
def home(request):
    """Home page view with simple analysis on POST - OPTIMIZED."""
    try:
        # Cache stocks for longer period
        cache_key_stocks = 'all_available_stocks_v2'
        available_stocks = cache.get(cache_key_stocks)
        if not available_stocks:
            stocks_dict = get_all_available_stocks()
            available_stocks = [(ticker, country) for ticker, country in stocks_dict.items()]
            cache.set(cache_key_stocks, available_stocks, timeout=1800)  # 30 minutes

        # Always build headline indices for the hero/ticker (cached for performance)
        cache_key_indices = 'market_indices_home_v2'
        market_indices = cache.get(cache_key_indices)
        if market_indices is None:
            market_indices = {}
            indices = {'^GSPC': 'SPX',
                       '^DJI': 'DJI', '^IXIC': 'IXIC'}
            # Fetch indices individually (faster than batch due to MultiIndex complexity)
            for symbol, display_symbol in indices.items():
                try:
                    t = yf.Ticker(symbol)
                    hist = t.history(period='2d', interval='1d')
                    if not hist.empty and len(hist) >= 2:
                        current = float(hist['Close'].iloc[-1])
                        prev_close = float(hist['Close'].iloc[0])
                        change = ((current - prev_close) /
                                  prev_close) * 100 if prev_close else 0.0
                        market_indices[display_symbol] = {
                            'price': round(current, 2),
                            'change': round(change, 2)
                        }
                except Exception as e:
                    print(f"Error fetching {display_symbol} data: {str(e)}")
            # Cache for 10 minutes (increased from 5)
            cache.set(cache_key_indices, market_indices, timeout=600)

        # Default context
        context = {
            'available_stocks': available_stocks,
            'market_indices': market_indices,
            'flag': False,
        }

        # Handle analysis form submission
        if request.method == 'POST':
            import re
            raw_symbol = (request.POST.get('company1') or '').strip().upper()
            # Accept inputs like "AAPL, MSFT" or " AAPL  " and take the first token
            tokens = [t for t in re.split(r"[\s,]+", raw_symbol) if t]
            symbol = tokens[0] if tokens else ''
            start_date = (request.POST.get('start_date') or '').strip()
            end_date = (request.POST.get('close_date') or '').strip()
            if symbol:
                # Check cache first
                cache_key_stock = f'stock_data_{symbol}_{start_date}_{end_date}'
                cached_stock_data = cache.get(cache_key_stock)
                if cached_stock_data:
                    context.update(cached_stock_data)
                    context['flag'] = True
                    return render(request, 'home2.html', context)

                try:
                    # Normalize dates
                    s = pd.to_datetime(
                        start_date, errors='coerce') if start_date else None
                    e = pd.to_datetime(
                        end_date, errors='coerce') if end_date else None
                    if s and e and e < s:
                        messages.error(
                            request, 'End date must be after start date.')
                        raise ValueError('Invalid date range')

                    # First attempt using Ticker().history (more reliable, no MultiIndex issues)
                    t = yf.Ticker(symbol)
                    try:
                        if s is None and e is None:
                            # Default to 6 months if no dates provided
                            hist = t.history(period='6mo', interval='1d')
                        else:
                            # Use provided date range
                            if s and e:
                                hist = t.history(start=s, end=e, interval='1d')
                            elif s:
                                hist = t.history(start=s, interval='1d')
                            elif e:
                                hist = t.history(end=e, interval='1d')
                            else:
                                hist = t.history(period='6mo', interval='1d')
                    except Exception as e1:
                        print(f"Ticker history failed: {e1}")
                        # Fallback to yf.download
                        try:
                            hist = yf.download(
                                symbol, start=s, end=e, progress=False, show_errors=False)
                            # yf.download returns MultiIndex for single symbol too, flatten it
                            if isinstance(hist.columns, pd.MultiIndex):
                                hist.columns = [col[0] if isinstance(
                                    col, tuple) else col for col in hist.columns]
                        except Exception as e2:
                            print(f"yf.download also failed: {e2}")
                            hist = None

                    # Try stooq as an additional free source
                    if (hist is None or hist.empty):
                        try:
                            from pandas_datareader import data as pdr
                            st_s = s.date() if s is not None else None
                            st_e = e.date() if e is not None else None
                            stooq = pdr.DataReader(symbol, 'stooq', st_s, st_e)
                            if stooq is not None and not stooq.empty:
                                stooq = stooq.sort_index()  # ascending
                                stooq = stooq.rename(columns={
                                    'Open': 'Open', 'High': 'High', 'Low': 'Low',
                                    'Close': 'Close', 'Volume': 'Volume',
                                    'open': 'Open', 'high': 'High', 'low': 'Low',
                                    'close': 'Close', 'volume': 'Volume'
                                })
                                hist = stooq
                        except Exception:
                            pass

                    if hist is None or hist.empty:
                        # Only show warning if we truly have no data
                        messages.warning(
                            request, f'No market data available for {symbol}. Please check the symbol and try again.')
                        # Don't create demo data - let the user know there's an issue
                        raise ValueError(f'No data available for {symbol}')

                    # Some returns use MultiIndex columns; flatten if needed
                    # For MultiIndex, take the first element (column name) not the last (ticker symbol)
                    if isinstance(hist.columns, pd.MultiIndex):
                        hist.columns = [c[0] if isinstance(c, tuple) and len(c) > 0 else (
                            c[-1] if isinstance(c, tuple) else c) for c in hist.columns]

                    # Normalize column names (yfinance may return lower case)
                    rename_map = {}
                    cols_lower = {str(c).lower(): c for c in hist.columns}
                    for want in ['open', 'high', 'low', 'close', 'volume', 'adj close']:
                        if want in cols_lower:
                            # map the existing column key to Title Case version, except Adj Close
                            new_name = 'Adj Close' if want == 'adj close' else want.title()
                            rename_map[cols_lower[want]] = new_name
                    if rename_map:
                        hist = hist.rename(columns=rename_map)

                    # If Close is still missing but Adj Close exists, use it
                    if 'Close' not in hist.columns and 'Adj Close' in hist.columns:
                        hist = hist.rename(columns={'Adj Close': 'Close'})

                    # Require Close column - this is essential
                    if 'Close' not in hist.columns:
                        # Try to find a close-like column
                        for col in hist.columns:
                            if 'close' in str(col).lower():
                                hist['Close'] = hist[col]
                                break

                        # Last resort: if there is any numeric column, treat it as Close
                        if 'Close' not in hist.columns:
                            numeric_cols = [
                                c for c in hist.columns if pd.api.types.is_numeric_dtype(hist[c])]
                            if numeric_cols:
                                hist['Close'] = hist[numeric_cols[0]]
                            else:
                                # If we can't find any data, raise an error
                                messages.error(
                                    request, f'Unable to retrieve pricing data for {symbol}. Please verify the symbol is correct.')
                                raise ValueError(
                                    f'No pricing data found for {symbol}')

                    hist = hist.dropna(subset=['Close'])
                    if hist.empty:
                        messages.error(
                            request, 'No closing prices available for the selected range.')
                        raise ValueError('No close data')

                    x = hist.index.tz_localize(
                        None).strftime('%Y-%m-%d').to_list()
                    close_s = hist['Close'].astype(float).round(2)
                    open_s = hist['Open'].astype(float).round(
                        2) if 'Open' in hist.columns else close_s
                    high_s = hist['High'].astype(float).round(
                        2) if 'High' in hist.columns else close_s
                    low_s = hist['Low'].astype(float).round(
                        2) if 'Low' in hist.columns else close_s
                    # Handle volume data - ensure it's properly formatted
                    if 'Volume' in hist.columns:
                        volume_s = hist['Volume'].fillna(0)
                        # Convert to numeric, handling any non-numeric values
                        volume_s = pd.to_numeric(
                            volume_s, errors='coerce').fillna(0)
                        # Convert to int64 for large numbers
                        volume_s = volume_s.astype('int64')
                        # Ensure no negative values
                        volume_s = volume_s.clip(lower=0)
                    else:
                        # If no volume column, try to get it from the ticker
                        try:
                            # Try to get volume from the same ticker
                            t_vol = yf.Ticker(symbol)
                            hist_vol = t_vol.history(
                                start=s if s else None, end=e if e else None, period='6mo' if not s and not e else None, interval='1d')
                            if 'Volume' in hist_vol.columns and not hist_vol.empty:
                                # Align volume data with price data by index
                                volume_s = hist_vol['Volume'].reindex(
                                    hist.index, fill_value=0)
                                volume_s = volume_s.fillna(0).astype('int64')
                            else:
                                volume_s = pd.Series(
                                    [0]*len(close_s), index=hist.index, dtype='int64')
                        except Exception as vol_err:
                            print(f"Volume fetch error: {vol_err}")
                            # Final fallback: zero volume
                            volume_s = pd.Series(
                                [0]*len(close_s), index=hist.index, dtype='int64')

                    # Convert to lists for template rendering, ensuring proper data types
                    y_open = [float(x) for x in open_s.to_list()]
                    y_close = [float(x) for x in close_s.to_list()]
                    y_high = [float(x) for x in high_s.to_list()]
                    y_low = [float(x) for x in low_s.to_list()]
                    # Convert volume to list, ensuring all values are valid integers
                    y_volume = [int(float(x)) if pd.notna(x) and float(
                        x) >= 0 else 0 for x in volume_s.to_list()]

                    first_close = float(hist['Close'].iloc[0])
                    last_close = float(hist['Close'].iloc[-1])
                    change_price = round(last_close - first_close, 2)
                    change_pct = round(
                        (change_price / first_close) * 100, 2) if first_close else 0.0

                    stock_context = {
                        'flag': True,
                        'company': symbol,
                        'x': x,
                        'y_open': y_open,
                        'y_close': y_close,
                        'y_high': y_high,
                        'y_low': y_low,
                        'y_volume': y_volume,
                        'last_day_price': round(last_close, 2),
                        'min_price': round(float(hist['Low'].min()), 2),
                        'max_price': round(float(hist['High'].max()), 2),
                        'change_in_price': change_price,
                        'change_in_precentage': change_pct,
                    }
                    context.update(stock_context)
                    # Cache stock data for 10 minutes
                    cache.set(cache_key_stock, stock_context, timeout=600)
                except Exception as e:
                    import traceback
                    error_msg = str(e)
                    print(f"Home analysis error for {symbol}: {error_msg}")
                    print(traceback.format_exc())
                    # Only show error if we haven't already shown a message
                    if 'No data available' not in error_msg and 'No pricing data' not in error_msg:
                        messages.error(
                            request, f'Error fetching data for {symbol}: {error_msg}. Please try again or check the symbol.')
                    # Don't create demo data - let the error message be shown to the user

        return render(request, 'home2.html', context)
    except Exception as e:
        print(f"Error in home view: {str(e)}")
        # Render minimal home page even if data fetching fails
        return render(request, 'home2.html', {
            'available_stocks': [],
            'market_indices': {},
            'flag': False,
        })


def compare(request):
    """Compare stocks view"""
    stocks_dict = get_all_available_stocks()
    available_stocks = [(ticker, country)
                        for ticker, country in stocks_dict.items()]

    context = {
        'available_stocks': available_stocks,
        'flag': False,
    }

    def fetch_stock_data(symbol, start=None, end=None, force_sample=False):
        data = load_stock_dataset(symbol, start=start, end=end, period='6mo', interval='1d', force_sample=force_sample)
        if not data:
            return None
        return {
            'x': data['x'],
            'y_open': data['y_open'],
            'y_close': data['y_close'],
            'y_high': data['y_high'],
            'y_low': data['y_low'],
            'y_volume': data['y_volume'],
            'last_day_price': data['last_day_price'],
            'min_price': data['min_price'],
            'max_price': data['max_price'],
            'change_in_price': data['change_in_price'],
            'change_in_precentage': data['change_in_precentage'],
            'df': data['df'],
            'df_values': data['df_values'],
            'used_sample': data['used_sample'],
            'data_symbol': data['data_symbol'],
        }

    def populate_compare_context(stock1_data, stock2_data, requested1, requested2, start_date, close_date, request_obj):
        if not stock1_data or not stock2_data:
            return

        dates1 = set(stock1_data['x'])
        dates2 = set(stock2_data['x'])
        common_dates = sorted(list(dates1.intersection(dates2)))
        stock1_dict = {date: idx for idx, date in enumerate(stock1_data['x'])}
        stock2_dict = {date: idx for idx, date in enumerate(stock2_data['x'])}

        if common_dates:
            stock1_aligned = {
                'y_open': [stock1_data['y_open'][stock1_dict[d]] for d in common_dates if d in stock1_dict],
                'y_close': [stock1_data['y_close'][stock1_dict[d]] for d in common_dates if d in stock1_dict],
                'y_high': [stock1_data['y_high'][stock1_dict[d]] for d in common_dates if d in stock1_dict],
                'y_low': [stock1_data['y_low'][stock1_dict[d]] for d in common_dates if d in stock1_dict],
                'y_volume': [stock1_data['y_volume'][stock1_dict[d]] for d in common_dates if d in stock1_dict],
            }
            stock2_aligned = {
                'y_open': [stock2_data['y_open'][stock2_dict[d]] for d in common_dates if d in stock2_dict],
                'y_close': [stock2_data['y_close'][stock2_dict[d]] for d in common_dates if d in stock2_dict],
                'y_high': [stock2_data['y_high'][stock2_dict[d]] for d in common_dates if d in stock2_dict],
                'y_low': [stock2_data['y_low'][stock2_dict[d]] for d in common_dates if d in stock2_dict],
                'y_volume': [stock2_data['y_volume'][stock2_dict[d]] for d in common_dates if d in stock2_dict],
            }
            stock1_data['y_open'] = stock1_aligned['y_open']
            stock1_data['y_close'] = stock1_aligned['y_close']
            stock1_data['y_high'] = stock1_aligned['y_high']
            stock1_data['y_low'] = stock1_aligned['y_low']
            stock1_data['y_volume'] = stock1_aligned['y_volume']
            stock2_data['y_open'] = stock2_aligned['y_open']
            stock2_data['y_close'] = stock2_aligned['y_close']
            stock2_data['y_high'] = stock2_aligned['y_high']
            stock2_data['y_low'] = stock2_aligned['y_low']
            stock2_data['y_volume'] = stock2_aligned['y_volume']
            stock1_data['df_values'] = [
                (stock1_data['y_open'][i], stock1_data['y_high'][i], stock1_data['y_low'][i],
                 stock1_data['y_close'][i], stock1_data['y_volume'][i], d)
                for i, d in enumerate(common_dates)
            ]
            stock2_data['df_values'] = [
                (stock2_data['y_open'][i], stock2_data['y_high'][i], stock2_data['y_low'][i],
                 stock2_data['y_close'][i], stock2_data['y_volume'][i], d)
                for i, d in enumerate(common_dates)
            ]
        else:
            common_dates = stock1_data['x']
            stock2_data['y_open'] = [0] * len(common_dates)
            stock2_data['y_high'] = [0] * len(common_dates)
            stock2_data['y_low'] = [0] * len(common_dates)
            stock2_data['y_close'] = [0] * len(common_dates)
            stock2_data['y_volume'] = [0] * len(common_dates)
            stock2_data['df_values'] = [
                (0, 0, 0, 0, 0, d) for d in common_dates
            ]

        stock1_data['x'] = common_dates
        stock2_data['x'] = common_dates

        def rebuild_dataframe(stock_data):
            stock_data['df'] = pd.DataFrame({
                'Open': stock_data['y_open'],
                'High': stock_data['y_high'],
                'Low': stock_data['y_low'],
                'Close': stock_data['y_close'],
                'Volume': stock_data['y_volume'],
                'Date': common_dates
            })
            if stock_data['y_close']:
                first_close = float(stock_data['y_close'][0])
                last_close = float(stock_data['y_close'][-1])
                stock_data['last_day_price'] = round(last_close, 2)
                stock_data['change_in_price'] = round(
                    last_close - first_close, 2)
                stock_data['change_in_precentage'] = round(
                    (stock_data['change_in_price'] / first_close) * 100, 2) if first_close else 0.0
                stock_data['min_price'] = round(
                    min(stock_data['y_low']), 2) if stock_data['y_low'] else 0.0
                stock_data['max_price'] = round(
                    max(stock_data['y_high']), 2) if stock_data['y_high'] else 0.0

        rebuild_dataframe(stock1_data)
        rebuild_dataframe(stock2_data)

        company1_display = stock1_data.get('data_symbol', requested1)
        company2_display = stock2_data.get('data_symbol', requested2)

        if stock1_data.get('used_sample') and request_obj is not None:
            messages.info(
                request_obj, f'Live data for {requested1} is unavailable. Showing demo data instead.')
        if stock2_data.get('used_sample') and request_obj is not None:
            messages.info(
                request_obj, f'Live data for {requested2} is unavailable. Showing demo data instead.')

        context.update({
            'flag': True,
            'company1': company1_display,
            'company2': company2_display,
            'company1_requested': requested1,
            'company2_requested': requested2,
            'start_date': start_date,
            'close_date': close_date,
            'x': json.dumps(common_dates),
            'y_open_stock1': json.dumps(stock1_data['y_open']),
            'y_close_stock1': json.dumps(stock1_data['y_close']),
            'y_high_stock1': json.dumps(stock1_data['y_high']),
            'y_low_stock1': json.dumps(stock1_data['y_low']),
            'y_volume_stock1': json.dumps(stock1_data['y_volume']),
            'last_day_price_stock1': stock1_data['last_day_price'],
            'min_price_stock1': stock1_data['min_price'],
            'max_price_stock1': stock1_data['max_price'],
            'change_in_price_stock1': stock1_data['change_in_price'],
            'change_in_precentage_stock1': stock1_data['change_in_precentage'],
            'df1': stock1_data['df'],
            'df1_values': stock1_data['df_values'],
            'y_open_stock2': json.dumps(stock2_data['y_open']),
            'y_close_stock2': json.dumps(stock2_data['y_close']),
            'y_high_stock2': json.dumps(stock2_data['y_high']),
            'y_low_stock2': json.dumps(stock2_data['y_low']),
            'y_volume_stock2': json.dumps(stock2_data['y_volume']),
            'last_day_price_stock2': stock2_data['last_day_price'],
            'min_price_stock2': stock2_data['min_price'],
            'max_price_stock2': stock2_data['max_price'],
            'change_in_price_stock2': stock2_data['change_in_price'],
            'change_in_precentage_stock2': stock2_data['change_in_precentage'],
            'df2': stock2_data['df'],
            'df2_values': stock2_data['df_values'],
        })

    # Handle comparison form submission - Post-Redirect-Get pattern
    if request.method == 'POST':
        company1 = (request.POST.get('company1') or '').strip().upper()
        company2 = (request.POST.get('company2') or '').strip().upper()
        start_date = (request.POST.get('start_date') or '').strip()
        close_date = (request.POST.get('close_date') or '').strip()

        if company1 and company2:
            try:
                # Normalize dates
                s = pd.to_datetime(
                    start_date, errors='coerce') if start_date else None
                e = pd.to_datetime(
                    close_date, errors='coerce') if close_date else None

                if s and e and e < s:
                    messages.error(
                        request, 'End date must be after start date.')
                    return render(request, 'template/compare3.html', context)

                # Fetch data for both stocks
                stock1_data = fetch_stock_data(company1, start=s, end=e)
                stock2_data = fetch_stock_data(company2, start=s, end=e)

                if stock1_data is None:
                    messages.error(
                        request, f'Unable to fetch data for {company1}. Please check the symbol.')
                    return render(request, 'template/compare3.html', context)

                if stock2_data is None:
                    messages.error(
                        request, f'Unable to fetch data for {company2}. Please check the symbol.')
                    return render(request, 'template/compare3.html', context)

                populate_compare_context(
                    stock1_data, stock2_data, company1, company2, start_date, close_date, request)
                
                # Store results in session and redirect (PRG pattern)
                session_data = {
                    'flag': context.get('flag', False),
                    'company1': context.get('company1', ''),
                    'company2': context.get('company2', ''),
                    'company1_requested': context.get('company1_requested', ''),
                    'company2_requested': context.get('company2_requested', ''),
                    'start_date': context.get('start_date', ''),
                    'close_date': context.get('close_date', ''),
                    'x': context.get('x', []),
                    'y_open_stock1': context.get('y_open_stock1', []),
                    'y_close_stock1': context.get('y_close_stock1', []),
                    'y_high_stock1': context.get('y_high_stock1', []),
                    'y_low_stock1': context.get('y_low_stock1', []),
                    'y_volume_stock1': context.get('y_volume_stock1', []),
                    'last_day_price_stock1': context.get('last_day_price_stock1', 0),
                    'min_price_stock1': context.get('min_price_stock1', 0),
                    'max_price_stock1': context.get('max_price_stock1', 0),
                    'change_in_price_stock1': context.get('change_in_price_stock1', 0),
                    'change_in_precentage_stock1': context.get('change_in_precentage_stock1', 0),
                    'df1_values': context.get('df1_values', []),
                    'y_open_stock2': context.get('y_open_stock2', []),
                    'y_close_stock2': context.get('y_close_stock2', []),
                    'y_high_stock2': context.get('y_high_stock2', []),
                    'y_low_stock2': context.get('y_low_stock2', []),
                    'y_volume_stock2': context.get('y_volume_stock2', []),
                    'last_day_price_stock2': context.get('last_day_price_stock2', 0),
                    'min_price_stock2': context.get('min_price_stock2', 0),
                    'max_price_stock2': context.get('max_price_stock2', 0),
                    'change_in_price_stock2': context.get('change_in_price_stock2', 0),
                    'change_in_precentage_stock2': context.get('change_in_precentage_stock2', 0),
                    'df2_values': context.get('df2_values', []),
                }
                request.session['compare_results'] = session_data
                # Also store for downloads (persist across navigation)
                request.session['compare_results_download'] = {
                    'company1': context.get('company1', ''),
                    'company2': context.get('company2', ''),
                    'df1_values': context.get('df1_values', []),
                    'df2_values': context.get('df2_values', []),
                }
                print(f"DEBUG: Saved to session. df1_values len: {len(context.get('df1_values', []))}, df2_values len: {len(context.get('df2_values', []))}")
                return redirect('compare')
            except Exception as e:
                import traceback
                print(f"Compare error: {e}")
                print(traceback.format_exc())
                messages.error(request, f'Error comparing stocks: {str(e)}')
    
    # Check for results in session (from redirect)
    if 'compare_results' in request.session:
        session_data = request.session.pop('compare_results')  # Remove after reading
        context.update(session_data)
    else:
        # Show demo data only on initial GET (not after redirect)
        default1, default2 = get_default_sample_symbols()
        sample1 = fetch_stock_data(default1, force_sample=True)
        sample2 = fetch_stock_data(default2, force_sample=True)
        if sample1 and sample2:
            populate_compare_context(
                sample1, sample2, default1, default2, '', '', None)
            # Store demo data for downloads too
            request.session['compare_results_download'] = {
                'company1': context.get('company1', default1),
                'company2': context.get('company2', default2),
                'df1_values': context.get('df1_values', []),
                'df2_values': context.get('df2_values', []),
            }

    return render(request, 'template/compare3.html', context)


def predict(request):
    """Predict stock prices view - OPTIMIZED"""
    # Cache available stocks
    cache_key_stocks = 'predict_available_stocks_v2'
    available_stocks = cache.get(cache_key_stocks)
    if not available_stocks:
        stocks_dict = get_all_available_stocks()
        available_stocks = [(ticker, country) for ticker, country in stocks_dict.items()]
        cache.set(cache_key_stocks, available_stocks, timeout=1800)  # 30 minutes

    context = {
        'available_stocks': available_stocks,
        'flag': False,
    }

    def build_prediction(symbol, days, force_sample=False):
        # Check cache first for faster response - longer cache time
        cache_key = f'prediction_{symbol}_{days}_v3'
        cached_result = cache.get(cache_key)
        if cached_result:
            print(f"Using cached prediction for {symbol}")
            return cached_result
        
        # Try using the Real ML Model first
        ml_predictions = MLService.predict_stock_price(symbol, days)
        
        if ml_predictions:
            # If ML service works, use its data
            # We still need historical data for the chart context
            try:
                t = yf.Ticker(symbol)
                hist = t.history(period='2mo', interval='1d')  # Reduced from 3mo to 2mo for speed
            except:
                hist = None

            if hist is None or hist.empty:
                 # Fallback if we can't get history even if we got predictions (unlikely but safe)
                 return None

            # Prepare historical data for chart
            hist = hist.sort_index()
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = [col[0] if isinstance(col, tuple) else col for col in hist.columns]
            
            # Ensure Close column exists
            if 'Close' not in hist.columns:
                 return None

            close_prices = hist['Close'].astype(float).values
            last_price = float(close_prices[-1])
            
            # Process predictions from ML Service
            predictions = ml_predictions # List of (date_str, price)
            predicted_prices = [p[1] for p in predictions]
            
            max_price = round(max(predicted_prices), 2)
            min_price = round(min(predicted_prices), 2)
            change_price = round(predicted_prices[-1] - last_price, 2)
            change_pct = round((change_price / last_price) * 100, 2) if last_price else 0.0
            
            # Simple Buy/Sell signal based on prediction
            buy = "Yes" if change_pct > 0 else "No"

            # Prepare historical data for chart - reduced to 15 days for speed
            hist_high = hist['High'].astype(float).values if 'High' in hist.columns else close_prices
            num_days = min(15, len(hist_high))  # Reduced from 20 to 15
            start_idx = len(hist_high) - num_days
            y_high_historical = [float(x) for x in hist_high[start_idx:]]
            x_historical = []
            hist_index = hist.index[start_idx:]
            for date in hist_index:
                if hasattr(date, 'tz_localize'):
                    try:
                        date = date.tz_localize(None)
                    except Exception:
                        date = date.tz_convert(None)
                elif hasattr(date, 'tz') and date.tz is not None:
                    date = date.replace(tzinfo=None)
                x_historical.append(date.strftime('%Y-%m-%d'))

            result = {
                'flag': True,
                'company': symbol.upper(),
                'requested_symbol': symbol.upper(),
                'days': days,
                'max_price': max_price,
                'min_price': min_price,
                'change_in_price': change_price,
                'change_in_precentage': change_pct,
                'buy': buy,
                'csv': predictions,  # List of (date, price) tuples
                'predicted_x': [p[0] for p in predictions],  # List of dates
                'predicted_y': predicted_prices,  # List of prices
                'x': x_historical,  # Historical dates
                'y_high': y_high_historical,  # Historical prices
                'y_close': y_high_historical,  # Use historical for close chart
                'used_sample': False,
            }
            
            # Cache result for 15 minutes (increased from 10)
            cache.set(cache_key, result, timeout=900)
            return result

        # --- FALLBACK TO HEURISTIC IF ML FAILS ---
        used_sample = False
        display_symbol = symbol.upper()
        hist = None

        if not force_sample:
            try:
                t = yf.Ticker(symbol)
                hist = t.history(period='3mo', interval='1d')  # Reduced from 6mo to 3mo
            except Exception as fetch_err:
                print(f"Prediction fetch error for {symbol}: {fetch_err}")
                hist = None

        if hist is None or hist.empty or 'Close' not in getattr(hist, 'columns', []):
            sample_history = get_sample_stock_history(symbol)
            fallback_symbol = None
            if sample_history is None:
                fallback_symbol = get_default_sample_symbols()[0]
                sample_history = get_sample_stock_history(fallback_symbol)
            if sample_history:
                used_sample = True
                display_symbol = fallback_symbol if fallback_symbol else symbol.upper()
                hist = pd.DataFrame(sample_history)
                hist['Date'] = pd.to_datetime(hist['Date'])
                hist = hist.set_index('Date')
            else:
                return None

        if isinstance(hist.columns, pd.MultiIndex):
            hist.columns = [col[0] if isinstance(
                col, tuple) else col for col in hist.columns]

        rename_map = {}
        cols_lower = {str(c).lower(): c for c in hist.columns}
        for want in ['open', 'high', 'low', 'close', 'volume']:
            if want in cols_lower:
                rename_map[cols_lower[want]] = want.title()
        if rename_map:
            hist = hist.rename(columns=rename_map)

        if 'Close' not in hist.columns:
            for col in hist.columns:
                if 'close' in str(col).lower():
                    hist['Close'] = hist[col]
                    break

        if 'Close' not in hist.columns:
            return None

        hist = hist.dropna(subset=['Close'])
        if hist.empty or len(hist) < 10:
            return None

        hist = hist.sort_index()
        close_prices = hist['Close'].astype(float).values

        ma_short_series = pd.Series(close_prices).rolling(
            window=10).mean().dropna()
        ma_long_series = pd.Series(close_prices).rolling(
            window=30).mean().dropna()
        ma_short = float(
            ma_short_series.iloc[-1]) if not ma_short_series.empty else float(close_prices[-1])
        ma_long = float(
            ma_long_series.iloc[-1]) if not ma_long_series.empty else float(close_prices[-1])

        recent_window = min(30, len(close_prices))
        recent_prices = close_prices[-recent_window:]
        if recent_prices[0] == 0:
            trend = 0.0
        else:
            trend = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]

        last_price = float(close_prices[-1])
        predictions = []

        last_date = hist.index[-1]
        if hasattr(last_date, 'tz_localize'):
            try:
                last_date = last_date.tz_localize(None)
            except Exception:
                last_date = last_date.tz_convert(None)
        elif hasattr(last_date, 'tz') and last_date.tz is not None:
            last_date = last_date.replace(tzinfo=None)

        for i in range(1, days + 1):
            future_date = last_date + timedelta(days=i)
            predicted_price = last_price * \
                (1 + (trend / max(recent_window, 1)) * i)
            volatility_window = min(30, len(close_prices))
            rolling_std = pd.Series(close_prices).rolling(
                window=volatility_window).std().dropna()
            volatility = float(
                rolling_std.iloc[-1]) / last_price if not rolling_std.empty and last_price else 0.02
            predicted_price = predicted_price * \
                (1 + np.random.normal(0, volatility * 0.1))
            predicted_price = max(predicted_price, last_price * 0.5)
            predicted_price = min(predicted_price, last_price * 2.0)
            predictions.append((future_date.strftime(
                '%Y-%m-%d'), round(predicted_price, 2)))

        predicted_prices = [p[1] for p in predictions]
        max_price = round(max(predicted_prices), 2)
        min_price = round(min(predicted_prices), 2)
        change_price = round(predicted_prices[-1] - last_price, 2)
        change_pct = round((change_price / last_price) *
                           100, 2) if last_price else 0.0
        buy = "Yes" if change_pct > 0 and ma_short > ma_long else "No"

        hist_high = hist['High'].astype(
            float).values if 'High' in hist.columns else close_prices
        num_days = min(30, len(hist_high))
        start_idx = len(hist_high) - num_days
        y_high_historical = [float(x) for x in hist_high[start_idx:]]
        x_historical = []
        hist_index = hist.index[start_idx:]
        for date in hist_index:
            if hasattr(date, 'tz_localize'):
                try:
                    date = date.tz_localize(None)
                except Exception:
                    date = date.tz_convert(None)
            elif hasattr(date, 'tz') and date.tz is not None:
                date = date.replace(tzinfo=None)
            x_historical.append(date.strftime('%Y-%m-%d'))

        return {
            'flag': True,
            'company': display_symbol,
            'requested_symbol': symbol.upper(),
            'days': days,
            'max_price': max_price,

            'min_price': min_price,
            'change_in_price': change_price,
            'change_in_precentage': change_pct,
            'buy': buy,
            'csv': predictions,
            'predicted_x': [p[0] for p in predictions],
            'predicted_y': predicted_prices,
            'x': x_historical,
            'y_high': y_high_historical,
            'y_close': predicted_prices,
            'used_sample': used_sample,
        }

    # Handle prediction form submission - Post-Redirect-Get pattern
    if request.method == 'POST':
        symbol = (request.POST.get('company1') or '').strip().upper()
        days_value = request.POST.get('days', '30')

        try:
            days_int = int(days_value)
            if days_int < 1 or days_int > 365:
                messages.error(request, 'Days must be between 1 and 365.')
                return render(request, 'predict.html', context)
        except ValueError:
            messages.error(request, 'Invalid number of days.')
            return render(request, 'predict.html', context)

        if not symbol:
            messages.error(request, 'Please provide a stock symbol.')
            return render(request, 'predict.html', context)

        try:
            prediction_context = build_prediction(symbol, days_int)
        except Exception as err:
            import traceback
            print(f"Predict error for {symbol}: {err}")
            print(traceback.format_exc())
            prediction_context = None

        if not prediction_context:
            messages.error(
                request, f'Unable to generate predictions for {symbol}. Showing demo data instead.')
            prediction_context = build_prediction(get_default_sample_symbols()[
                                                  0], days_int, force_sample=True)

        if prediction_context:
            context.update(prediction_context)
            if prediction_context.get('used_sample'):
                requested = prediction_context.get('requested_symbol', symbol)
                display = prediction_context.get('company', requested)
                messages.info(
                    request, f'Live data for {requested} is unavailable. Showing demo prediction for {display}.')
            
            
            # Store results in session and redirect (PRG pattern)
            # JSON serialize lists for proper JavaScript rendering
            import json
            session_data = {
                'flag': context.get('flag', False),
                'company': context.get('company', ''),
                'requested_symbol': context.get('requested_symbol', ''),
                'days': context.get('days', 30),
                'max_price': context.get('max_price', 0),
                'min_price': context.get('min_price', 0),
                'change_in_price': context.get('change_in_price', 0),
                'change_in_precentage': context.get('change_in_precentage', 0),
                'buy': context.get('buy', 'No'),
                'csv': context.get('csv', []),
                'predicted_x': json.dumps(context.get('predicted_x', [])),
                'predicted_y': json.dumps(context.get('predicted_y', [])),
                'x': json.dumps(context.get('x', [])),
                'y_high': json.dumps(context.get('y_high', [])),
                'y_close': json.dumps(context.get('y_close', [])),
                'used_sample': context.get('used_sample', False),
            }
            request.session['predict_results'] = session_data
            return redirect('predict')
    
    # Check for results in session (from redirect)
    if 'predict_results' in request.session:
        session_data = request.session.pop('predict_results')  # Remove after reading
        context.update(session_data)
    # If no results in session, flag is already False from initial context
    # This ensures the form shows when page is refreshed or visited fresh

    return render(request, 'predict.html', context)


def details(request, id):
    """Stock details view"""
    stocks_dict = get_all_available_stocks()
    available_stocks = [(ticker, country)
                        for ticker, country in stocks_dict.items()]

    requested_symbol = (id or '').strip().upper()
    dataset = load_stock_dataset(requested_symbol, period='1y', interval='1d')

    fallback_used = False
    if not dataset:
        fallback_symbol = get_default_sample_symbols()[0]
        dataset = load_stock_dataset(fallback_symbol, period='1y', interval='1d', force_sample=True)
        fallback_used = True
    elif dataset.get('used_sample'):
        fallback_used = True

    if not dataset:
        messages.error(request, 'Unable to load stock details at this time.')
        return redirect('all_stocks')

    if fallback_used:
        messages.info(
            request,
            f'Historical data unavailable for {requested_symbol}. Using demo historical data, but current price is live.',
        )
    else:
        messages.success(
            request,
            f'Showing live market data for {requested_symbol}.',
        )

    context = {
        'stock_id': requested_symbol,
        'available_stocks': available_stocks,
        'company': dataset['data_symbol'],
        'requested_symbol': requested_symbol,
        'last_day_price': dataset['last_day_price'],
        'current_live_price': dataset.get('current_live_price'),
        'is_live_price': dataset.get('current_live_price') is not None,
        'max_price': dataset['max_price'],
        'min_price': dataset['min_price'],
        'change_in_price': dataset['change_in_price'],
        'change_in_precentage': dataset['change_in_precentage'],
        'x': dataset['x'],
        'y_high': dataset['y_high'],
        'y_low': dataset['y_low'],
        'y_open': dataset['y_open'],
        'y_close': dataset['y_close'],
        'y_volume': dataset['y_volume'],
        'df': dataset['df'],
        'description': dataset['description'],
    }

    return render(request, 'template/details.html', context)


def all_stocks(request):
    """All stocks view - browse and search stocks"""
    stocks_dict = get_all_available_stocks()
    available_stocks = [(ticker, country)
                        for ticker, country in stocks_dict.items()]

    # Always show popular stocks by default (cached)
    cache_key_popular = 'popular_stocks_data'
    stocks_data = cache.get(cache_key_popular)

    if stocks_data is None:
        # Fetch popular stocks
        popular_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META',
                           'NVDA', 'NFLX', 'JPM', 'BAC', 'V', 'WMT', 'JNJ', 'PG', 'MA']
        stocks_data = []
        for ticker in popular_tickers:
            try:
                t = yf.Ticker(ticker)
                try:
                    fi = t.fast_info
                    current_price = float(
                        fi.get('lastPrice') or fi.get('regularMarketPrice') or 0)
                    previous_close = float(fi.get('previousClose') or 0)
                    high = float(fi.get('dayHigh') or current_price)
                    low = float(fi.get('dayLow') or current_price)
                    volume = int(fi.get('regularMarketVolume') or 0)
                except:
                    info = t.info
                    current_price = float(
                        info.get('currentPrice') or info.get('regularMarketPrice') or 0)
                    previous_close = float(
                        info.get('previousClose') or current_price)
                    high = float(info.get('dayHigh') or current_price)
                    low = float(info.get('dayLow') or current_price)
                    volume = int(info.get('volume') or 0)

                net_change = round(
                    current_price - previous_close, 2) if previous_close else 0
                percent_change = round(
                    (net_change / previous_close * 100), 2) if previous_close else 0

                try:
                    info = t.info
                    name = info.get('shortName') or info.get(
                        'longName') or ticker
                except:
                    name = ticker

                stocks_data.append({
                    'symbol': ticker,
                    'name': name,
                    'close': current_price,
                    'net_change': net_change,
                    'percent_change': percent_change,
                    'high': high,
                    'low': low,
                    'volume': volume,
                })
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                continue

        if not stocks_data:
            stocks_data = get_sample_browse_stocks()
        # Cache for 15 minutes
        cache.set(cache_key_popular, stocks_data, timeout=900)

    context = {
        'available_stocks': available_stocks,
        'stocks_data': stocks_data,
    }

    # Handle search form submission - Post-Redirect-Get pattern
    if request.method == 'POST':
        search_query = (request.POST.get('search') or '').strip().upper()

        if search_query:
            # Find matching stocks
            matching_stocks = []
            for ticker, country in available_stocks:
                if search_query in ticker.upper():
                    matching_stocks.append((ticker, country))

            if matching_stocks:
                # Fetch data for matching stocks (limit to 20 for performance)
                search_stocks_data = []
                for ticker, country in matching_stocks[:20]:
                    try:
                        t = yf.Ticker(ticker)
                        # Use fast_info for quick data
                        try:
                            fi = t.fast_info
                            current_price = float(
                                fi.get('lastPrice') or fi.get('regularMarketPrice') or 0)
                            previous_close = float(
                                fi.get('previousClose') or 0)
                            high = float(fi.get('dayHigh') or current_price)
                            low = float(fi.get('dayLow') or current_price)
                            volume = int(fi.get('regularMarketVolume') or 0)
                        except:
                            # Fallback to info
                            info = t.info
                            current_price = float(
                                info.get('currentPrice') or info.get('regularMarketPrice') or 0)
                            previous_close = float(
                                info.get('previousClose') or current_price)
                            high = float(info.get('dayHigh') or current_price)
                            low = float(info.get('dayLow') or current_price)
                            volume = int(info.get('volume') or 0)

                        # Calculate change
                        net_change = round(
                            current_price - previous_close, 2) if previous_close else 0
                        percent_change = round(
                            (net_change / previous_close * 100), 2) if previous_close else 0

                        # Get company name
                        try:
                            info = t.info
                            name = info.get('shortName') or info.get(
                                'longName') or ticker
                        except:
                            name = ticker

                        search_stocks_data.append({
                            'symbol': ticker,
                            'name': name,
                            'close': current_price,
                            'net_change': net_change,
                            'percent_change': percent_change,
                            'high': high,
                            'low': low,
                            'volume': volume,
                        })
                    except Exception as e:
                        print(f"Error fetching data for {ticker}: {e}")
                        continue

                if search_stocks_data:
                    context['stocks_data'] = search_stocks_data
                else:
                    # Fallback to sample data filtered by query
                    sample_matches = [
                        stock for stock in get_sample_browse_stocks()
                        if search_query in stock['symbol'].upper()
                    ]
                    if sample_matches:
                        messages.info(
                            request, f'Live data unavailable. Showing demo results for "{search_query}".')
                        context['stocks_data'] = sample_matches
                    else:
                        messages.info(
                            request, f'No stocks found matching "{search_query}".')
            else:
                sample_matches = [
                    stock for stock in get_sample_browse_stocks()
                    if search_query in stock['symbol'].upper()
                ]
                if sample_matches:
                    messages.info(
                        request, f'No live matches for "{search_query}". Showing demo results instead.')
                    context['stocks_data'] = sample_matches
                else:
                    messages.info(
                        request, f'No stocks found matching "{search_query}".')
            
            # Store search results in session and redirect (PRG pattern)
            request.session['browse_search_query'] = search_query
            request.session['browse_results'] = context.get('stocks_data', [])
            return redirect('all_stocks')
    
    # Check for search results in session (from redirect)
    if 'browse_results' in request.session:
        context['stocks_data'] = request.session.pop('browse_results')
        search_query = request.session.pop('browse_search_query', '')
        # Keep search query in form if needed
        if search_query:
            context['search_query'] = search_query

    return render(request, 'all_stocks.html', context)


def download(request, id):
    """Download stock data from comparison"""
    import csv
    from django.http import HttpResponse
    
    # Get comparison data from session
    compare_data = request.session.get('compare_results_download', {})
    
    if not compare_data:
        return HttpResponse("No comparison data available. Please run a comparison first.", status=400)
    
    # Determine which stock to download
    if id == '1':
        company = compare_data.get('company1', 'Stock1')
        df_values = compare_data.get('df1_values', [])
    elif id == '2':
        company = compare_data.get('company2', 'Stock2')
        df_values = compare_data.get('df2_values', [])
    else:
        return HttpResponse("Invalid stock ID. Use 1 or 2.", status=400)
    
    if not df_values:
        return HttpResponse(f"No data available for {company}", status=400)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{company}_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    
    # Write data rows
    for row in df_values:
        if len(row) >= 6:
            # Format: (open, high, low, close, volume, date)
            open_price, high, low, close, volume, date = row
            writer.writerow([date, open_price, high, low, close, volume])
    
    return response


# Auth Views
def login_view(request):
    """Login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def register_view(request):
    """Register view"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password_confirm', '')
        email = request.POST.get('email', '').strip()
        
        # Validation
        if not username:
            messages.error(request, 'Username is required.')
            return render(request, 'register.html')
        
        if not email:
            messages.error(request, 'Email is required.')
            return render(request, 'register.html')
        
        if not password:
            messages.error(request, 'Password is required.')
            return render(request, 'register.html')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'register.html')
        
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return render(request, 'register.html')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Please use another or sign in.')
            return render(request, 'register.html')
        
        try:
            user = User.objects.create_user(
                username=username, password=password, email=email)
            login(request, user)
            messages.success(request, f'Welcome {username}! Your account has been created successfully.')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'register.html')
    
    return render(request, 'register.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    """Dashboard view - OPTIMIZED"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Cache available stocks for longer (1 hour)
    cache_key_stocks = 'dashboard_available_stocks'
    available_stocks = cache.get(cache_key_stocks)
    if not available_stocks:
        stocks_dict = get_all_available_stocks()
        available_stocks = [(ticker, country) for ticker, country in stocks_dict.items()]
        cache.set(cache_key_stocks, available_stocks, timeout=3600)
    
    # Fetch user's watchlist with optimized query - only selected fields
    watchlist_items = Watchlist.objects.filter(user=request.user).only('id', 'ticker', 'created_at').order_by('-created_at')[:10]
    watchlist_data = []
    
    def fetch_watchlist_item(item):
        cache_key = f'watchlist_{item.ticker}_v2'
        cached = cache.get(cache_key)
        if cached:
            cached['id'] = item.id
            return cached
        
        try:
            t = yf.Ticker(item.ticker)
            fast_info = t.fast_info
            current_price = float(fast_info.get('lastPrice') or fast_info.get('regularMarketPrice') or 0)
            previous_close = float(fast_info.get('previousClose') or 0)
            change = current_price - previous_close if previous_close else 0
            change_pct = (change / previous_close * 100) if previous_close else 0
            
            data = {
                'ticker': item.ticker,
                'price': current_price,
                'change': change,
                'change_pct': change_pct,
                'id': item.id
            }
            cache.set(cache_key, data, timeout=300)  # Cache for 5 min (increased)
            return data
        except Exception as e:
            print(f"Error fetching data for watchlist item {item.ticker}: {e}")
            return {
                'ticker': item.ticker,
                'price': 0,
                'change': 0,
                'change_pct': 0,
                'id': item.id
            }
    
    # Fetch watchlist items concurrently with increased workers
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_watchlist_item, item) for item in watchlist_items]
        for future in as_completed(futures):
            watchlist_data.append(future.result())

    return render(request, 'dashboard.html', {
        'available_stocks': available_stocks,
        'watchlist': watchlist_data
    })

@login_required
def add_to_watchlist(request, ticker):
    ticker = ticker.upper().strip()
    if ticker:
        # Check if already exists
        if not Watchlist.objects.filter(user=request.user, ticker=ticker).exists():
            Watchlist.objects.create(user=request.user, ticker=ticker)
            messages.success(request, f'{ticker} added to watchlist.')
        else:
            messages.info(request, f'{ticker} is already in your watchlist.')
    return redirect('dashboard')

@login_required
def remove_from_watchlist(request, ticker):
    ticker = ticker.upper().strip()
    Watchlist.objects.filter(user=request.user, ticker=ticker).delete()
    messages.success(request, f'{ticker} removed from watchlist.')
    return redirect('dashboard')


# Market Status Functions
def get_market_status(ticker):
    """Get market status (open/closed) for a given ticker"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        timezone_str = info.get('exchangeTimezoneName', 'America/New_York')
        if pytz:
            try:
                tz = pytz.timezone(timezone_str)
            except:
                tz = pytz.timezone('America/New_York')
            market_time = datetime.now(tz)
        else:
            market_time = datetime.now()
            tz = None

        market_hour = market_time.hour
        market_day = market_time.weekday()

        if market_day >= 5:
            return {
                'is_open': False,
                'status': 'closed',
                'message': 'Market is closed (Weekend)',
                'next_open': None,
                'current_time': market_time.strftime('%Y-%m-%d %H:%M:%S %Z')
            }

        if 9 <= market_hour < 16:
            return {
                'is_open': True,
                'status': 'open',
                'message': 'Market is currently open',
                'next_close': None,
                'current_time': market_time.strftime('%Y-%m-%d %H:%M:%S %Z')
            }
        else:
            return {
                'is_open': False,
                'status': 'closed',
                'message': 'Market is closed',
                'next_open': None,
                'current_time': market_time.strftime('%Y-%m-%d %H:%M:%S %Z')
            }
    except Exception as e:
        return {
            'is_open': None,
            'status': 'unknown',
            'message': f'Unable to determine market status: {str(e)}',
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


# Live Price APIs
def live_price_api(request):
    """API endpoint for live stock price updates (cached for 30 seconds)"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    ticker = request.GET.get('ticker', '').strip().upper()
    if not ticker:
        return JsonResponse({'error': 'Ticker symbol required'}, status=400)

    # Check cache first (30 second cache for live data)
    cache_key = f'live_price_{ticker}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data)

    try:
        stock = yf.Ticker(ticker)

        try:
            fast_info = stock.fast_info
            current_price = fast_info.get('lastPrice', 0)
            previous_close = fast_info.get('previousClose', 0)
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close *
                              100) if previous_close else 0
            volume = fast_info.get('regularMarketVolume', 0)
            high = fast_info.get('dayHigh', 0)
            low = fast_info.get('dayLow', 0)
        except:
            info = stock.info
            current_price = info.get(
                'currentPrice', info.get('regularMarketPrice', 0))
            previous_close = info.get('previousClose', 0)
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close *
                              100) if previous_close else 0
            volume = info.get('volume', 0)
            high = info.get('dayHigh', 0)
            low = info.get('dayLow', 0)

        market_status = get_market_status(ticker)

        try:
            hist = stock.history(period='1d', interval='1m')
            if not hist.empty:
                latest_data = hist.iloc[-1]
                timestamp = latest_data.name.strftime('%Y-%m-%d %H:%M:%S')
            else:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        response_data = {
            'success': True,
            'ticker': ticker,
            'price': round(current_price, 2),
            'previous_close': round(previous_close, 2),
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'volume': int(volume),
            'high': round(high, 2),
            'low': round(low, 2),
            'timestamp': timestamp,
            'market_status': market_status
        }
        # Cache for 30 seconds
        cache.set(cache_key, response_data, timeout=30)
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'ticker': ticker
        }, status=500)


def market_status_api(request):
    """API endpoint for market status"""
    ticker = request.GET.get('ticker', '').strip().upper()
    if not ticker:
        return JsonResponse({'error': 'Ticker symbol required'}, status=400)

    status = get_market_status(ticker)
    return JsonResponse(status)


def live_prices_batch_api(request):
    """API endpoint for batch live price updates"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    tickers_str = request.GET.get('tickers', '')
    if not tickers_str:
        return JsonResponse({'error': 'Tickers required (comma-separated)'}, status=400)

    tickers = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    if not tickers:
        return JsonResponse({'error': 'No valid tickers provided'}, status=400)

    results = {}
    for ticker in tickers[:10]:
        try:
            stock = yf.Ticker(ticker)
            try:
                fast_info = stock.fast_info
                current_price = fast_info.get('lastPrice', 0)
                previous_close = fast_info.get('previousClose', 0)
                change = current_price - previous_close if previous_close else 0
                change_percent = (change / previous_close *
                                  100) if previous_close else 0
                volume = fast_info.get('regularMarketVolume', 0)
                high = fast_info.get('dayHigh', 0)
                low = fast_info.get('dayLow', 0)
            except Exception:
                info = stock.info
                current_price = info.get(
                    'currentPrice', info.get('regularMarketPrice', 0))
                previous_close = info.get('previousClose', 0)
                change = current_price - previous_close if previous_close else 0
                change_percent = (change / previous_close *
                                  100) if previous_close else 0
                volume = info.get('volume', 0)
                high = info.get('dayHigh', 0)
                low = info.get('dayLow', 0)

            results[ticker] = {
                'success': True,
                'price': round(current_price, 2),
                'previous_close': round(previous_close, 2) if previous_close else None,
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': int(volume) if volume else 0,
                'high': round(high, 2) if high else None,
                'low': round(low, 2) if low else None
            }
        except Exception as e:
            results[ticker] = {'success': False, 'error': str(e)}

    return JsonResponse({'results': results})


# ============================================================================
# ALERT MANAGEMENT VIEWS
# ============================================================================

@login_required
def alert_settings(request):
    """Alert settings and management page"""
    from .models import UserAlertPreferences, PriceAlert
    from decimal import Decimal
    
    # Get or create user alert preferences
    prefs, created = UserAlertPreferences.objects.get_or_create(user=request.user)
    
    # Handle form submission
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_preferences':
            prefs.email_alerts_enabled = request.POST.get('email_alerts_enabled') == 'on'
            prefs.alert_frequency = request.POST.get('alert_frequency', 'realtime')
            
            # Handle quiet hours
            quiet_start = request.POST.get('quiet_hours_start')
            quiet_end = request.POST.get('quiet_hours_end')
            
            if quiet_start:
                prefs.quiet_hours_start = quiet_start
            if quiet_end:
                prefs.quiet_hours_end = quiet_end
            
            prefs.save()
            messages.success(request, '✓ Alert preferences updated successfully!')
            
        elif action == 'update_watchlist_alert':
            watchlist_id = request.POST.get('watchlist_id')
            from django.shortcuts import get_object_or_404
            watchlist_item = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
            
            watchlist_item.alert_enabled = request.POST.get('alert_enabled') == 'on'
            watchlist_item.alert_on_rise = request.POST.get('alert_on_rise') == 'on'
            watchlist_item.alert_on_fall = request.POST.get('alert_on_fall') == 'on'
            watchlist_item.alert_threshold_percent = Decimal(request.POST.get('alert_threshold_percent', '5.0'))
            watchlist_item.save()
            
            messages.success(request, f'✓ Alert settings updated for {watchlist_item.ticker}!')
        
        return redirect('alert_settings')
    
    # Get user's watchlist with alert info (exclude empty tickers)
    watchlist_items = Watchlist.objects.filter(
        user=request.user,
        ticker__isnull=False
    ).exclude(ticker='').order_by('-created_at')
    
    # Get recent alerts
    recent_alerts = PriceAlert.objects.filter(
        watchlist_item__user=request.user
    ).select_related('watchlist_item').order_by('-sent_at')[:20]
    
    context = {
        'preferences': prefs,
        'watchlist_items': watchlist_items,
        'recent_alerts': recent_alerts,
        'total_alerts': PriceAlert.objects.filter(watchlist_item__user=request.user).count(),
    }
    
    return render(request, 'template/alert_settings.html', context)


@login_required
def toggle_alert(request, watchlist_id):
    """Quick toggle alert for a watchlist item"""
    from django.shortcuts import get_object_or_404
    watchlist_item = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    watchlist_item.alert_enabled = not watchlist_item.alert_enabled
    watchlist_item.save()
    
    status = "enabled" if watchlist_item.alert_enabled else "disabled"
    messages.success(request, f'Alerts {status} for {watchlist_item.ticker}')
    
    return redirect('dashboard')


@login_required
def test_alert(request):
    """Send a test alert email to the user"""
    if request.method == 'POST':
        try:
            # Check if user has any watchlist items
            watchlist_item = Watchlist.objects.filter(user=request.user).first()
            
            if not watchlist_item:
                return JsonResponse({
                    'success': False,
                    'message': 'Please add at least one stock to your watchlist first'
                })
            
            # Send a test alert
            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings
            
            subject = "🎉 Test Alert from InsightTracker"
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 20px auto; padding: 30px; background: #f9fafb; border-radius: 12px; }}
        .header {{ background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%); color: white; padding: 30px; text-align: center; border-radius: 8px; margin-bottom: 20px; }}
        .content {{ background: white; padding: 30px; border-radius: 8px; }}
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">🎉 Test Alert</h1>
            <p style="margin: 10px 0 0 0;">Your email alerts are working perfectly!</p>
        </div>
        <div class="content">
            <p>Hi {request.user.username},</p>
            <p>This is a test email to confirm that your stock price alerts are configured correctly.</p>
            <p><strong>What happens next?</strong></p>
            <ul>
                <li>We'll monitor your watchlist stocks continuously</li>
                <li>You'll receive alerts when prices move beyond your threshold</li>
                <li>Alerts respect your quiet hours settings</li>
            </ul>
            <p>Currently watching: <strong>{Watchlist.objects.filter(user=request.user).count()} stocks</strong></p>
        </div>
        <div class="footer">
            <p>InsightTracker - AI-Powered Stock Analysis</p>
        </div>
    </div>
</body>
</html>
"""
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body="Test alert from InsightTracker",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[request.user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            return JsonResponse({
                'success': True,
                'message': f'Test email sent to {request.user.email}! Check your inbox.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error sending test email: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def bulk_toggle_alerts(request):
    """Enable or disable all alerts at once"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            enable = data.get('enable', True)
            
            # Update all watchlist items for the user
            updated_count = Watchlist.objects.filter(user=request.user).update(
                alert_enabled=enable
            )
            
            action = "enabled" if enable else "disabled"
            return JsonResponse({
                'success': True,
                'message': f'Successfully {action} {updated_count} alerts'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def bulk_adjust_thresholds(request):
    """Adjust all alert thresholds at once"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            adjustment = Decimal(str(data.get('adjustment', 0)))
            adjustment_type = data.get('type', 'increase')
            
            watchlist_items = Watchlist.objects.filter(user=request.user, alert_enabled=True)
            updated_count = 0
            
            for item in watchlist_items:
                if adjustment_type == 'increase':
                    item.alert_threshold_percent += adjustment
                elif adjustment_type == 'decrease':
                    item.alert_threshold_percent = max(Decimal('0.1'), item.alert_threshold_percent - adjustment)
                elif adjustment_type == 'set':
                    item.alert_threshold_percent = adjustment
                
                # Cap at reasonable values
                item.alert_threshold_percent = max(Decimal('0.1'), min(Decimal('100'), item.alert_threshold_percent))
                item.save()
                updated_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully adjusted thresholds for {updated_count} alerts'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def export_alert_history(request):
    """Export alert history as CSV"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    from .models import PriceAlert
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="alert_history_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Time', 'Stock', 'Alert Type', 'Price', 'Change %', 'Message'])
    
    # Get all user alerts
    alerts = PriceAlert.objects.filter(
        watchlist_item__user=request.user
    ).select_related('watchlist_item').order_by('-sent_at')[:1000]  # Limit to last 1000
    
    for alert in alerts:
        writer.writerow([
            alert.sent_at.strftime('%Y-%m-%d'),
            alert.sent_at.strftime('%H:%M:%S'),
            alert.watchlist_item.ticker,
            alert.alert_type,
            f'${alert.price_at_alert:.2f}' if alert.price_at_alert else 'N/A',
            f'{alert.percent_change:.2f}%' if alert.percent_change else 'N/A',
            alert.message[:100]  # Truncate long messages
        ])
    
    return response


# ============================================================================
# PORTFOLIO TRACKER VIEWS
# ============================================================================

@login_required
def portfolio_dashboard(request):
    """Portfolio overview dashboard"""
    from .models import Portfolio
    from .portfolio_service import PortfolioService
    
    # Get or create default portfolio (handle duplicates)
    try:
        portfolio = Portfolio.objects.filter(
            user=request.user,
            name="My Portfolio"
        ).first()
        
        if not portfolio:
            portfolio = Portfolio.objects.create(
                user=request.user,
                name="My Portfolio",
                description='Primary investment portfolio'
            )
    except Exception as e:
        # Fallback: just get the first portfolio for this user
        portfolio = Portfolio.objects.filter(user=request.user).first()
        if not portfolio:
            portfolio = Portfolio.objects.create(
                user=request.user,
                name="My Portfolio",
                description='Primary investment portfolio'
            )
    
    # Get portfolio summary
    summary = PortfolioService.get_portfolio_summary(portfolio)
    allocations = PortfolioService.get_portfolio_allocation(portfolio)
    recent_transactions = PortfolioService.get_recent_transactions(portfolio, limit=10)
    diversification_score = PortfolioService.get_diversification_score(portfolio)
    
    context = {
        'portfolio': portfolio,
        'summary': summary,
        'allocations': allocations,
        'recent_transactions': recent_transactions,
        'diversification_score': diversification_score,
    }
    
    return render(request, 'template/portfolio_dashboard.html', context)


@login_required
def add_holding(request):
    """Add a new stock holding to portfolio"""
    if request.method == 'POST':
        from .models import Portfolio
        from .portfolio_service import PortfolioService
        from decimal import Decimal
        from datetime import datetime
        
        try:
            # Get portfolio (handle duplicates)
            portfolio = Portfolio.objects.filter(user=request.user, name="My Portfolio").first()
            
            if not portfolio:
                portfolio = Portfolio.objects.create(
                    user=request.user,
                    name="My Portfolio",
                    description='Primary investment portfolio'
                )
            
            ticker = request.POST.get('ticker').upper()
            shares = Decimal(request.POST.get('shares'))
            purchase_price = Decimal(request.POST.get('purchase_price'))
            purchase_date = request.POST.get('purchase_date')
            notes = request.POST.get('notes', '')
            
            PortfolioService.add_holding(
                portfolio, ticker, shares, purchase_price, purchase_date, notes
            )
            
            messages.success(request, f'✓ Added {shares} shares of {ticker} to portfolio!')
            
        except Exception as e:
            messages.error(request, f'Error adding holding: {str(e)}')
    
    return redirect('portfolio_dashboard')


@login_required
def sell_holding(request, holding_id):
    """Sell shares from a holding"""
    if request.method == 'POST':
        from .models import PortfolioHolding
        from .portfolio_service import PortfolioService
        from decimal import Decimal
        from django.shortcuts import get_object_or_404
        
        try:
            holding = get_object_or_404(PortfolioHolding, id=holding_id, portfolio__user=request.user)
            
            shares = Decimal(request.POST.get('shares'))
            sell_price = Decimal(request.POST.get('sell_price'))
            sell_date = request.POST.get('sell_date')
            notes = request.POST.get('notes', '')
            
            PortfolioService.sell_holding(holding, shares, sell_price, sell_date, notes)
            
            messages.success(request, f'✓ Sold {shares} shares of {holding.ticker}!')
            
        except Exception as e:
            messages.error(request, f'Error selling shares: {str(e)}')
    
    return redirect('portfolio_dashboard')


@login_required
def delete_holding(request, holding_id):
    """Delete a holding from portfolio"""
    from .models import PortfolioHolding
    from django.shortcuts import get_object_or_404
    
    holding = get_object_or_404(PortfolioHolding, id=holding_id, portfolio__user=request.user)
    ticker = holding.ticker
    holding.delete()
    
    messages.success(request, f'✓ Removed {ticker} from portfolio!')
    return redirect('portfolio_dashboard')


# ============================================================================
# NEWS SENTIMENT VIEWS
# ============================================================================

@require_GET
def stock_news(request, ticker):
    """Get news articles for a stock with sentiment analysis"""
    from .news_service import NewsSentimentService
    
    ticker = ticker.upper()
    force_refresh = request.GET.get('refresh', '').lower() == 'true'
    
    # Fetch news with sentiment
    articles = NewsSentimentService.fetch_news(ticker, force_refresh=force_refresh)
    
    # Get aggregate sentiment
    sentiment_summary = NewsSentimentService.get_aggregate_sentiment(ticker, days=7)
    
    # Format articles for JSON response
    articles_data = [{
        'id': article.id,
        'title': article.title,
        'description': article.description,
        'url': article.url,
        'source': article.source,
        'published_at': article.published_at.strftime('%Y-%m-%d %H:%M'),
        'image_url': article.image_url,
        'sentiment_score': float(article.sentiment_score),
        'sentiment_label': article.sentiment_label,
    } for article in articles]
    
    return JsonResponse({
        'ticker': ticker,
        'articles': articles_data,
        'sentiment_summary': sentiment_summary,
        'total_articles': len(articles_data)
    })


@require_GET
def sentiment_trend(request, ticker):
    """Get sentiment trend data for charting"""
    from .news_service import NewsSentimentService
    
    ticker = ticker.upper()
    days = int(request.GET.get('days', 30))
    
    trend = NewsSentimentService.get_sentiment_trend(ticker, days=days)
    
    return JsonResponse({
        'ticker': ticker,
        'trend': trend
    })


# ============================================================================
# STOCK SCREENER VIEWS
# ============================================================================

@login_required
def stock_screener(request):
    """Stock screener page"""
    from .screener_service import StockScreenerService
    
    # Get preset screens
    presets = StockScreenerService.get_preset_screens()
    
    context = {
        'presets': presets,
    }
    
    return render(request, 'template/stock_screener.html', context)


@login_required
def run_screener(request):
    """Run stock screening with criteria"""
    if request.method == 'POST':
        from .screener_service import StockScreenerService
        import json
        
        try:
            # Parse criteria from request
            data = json.loads(request.body)
            criteria = data.get('criteria', {})
            ticker_list = data.get('ticker_list', None)
            
            # Convert string values to appropriate types
            for key, value in criteria.items():
                if key.startswith('min_') or key.startswith('max_'):
                    try:
                        criteria[key] = float(value) if value else None
                    except:
                        pass
            
            # Remove None values
            criteria = {k: v for k, v in criteria.items() if v is not None and v != ''}
            
            # Run screening
            results = StockScreenerService.screen_stocks(criteria, ticker_list)
            
            return JsonResponse({
                'success': True,
                'results': results,
                'count': len(results),
                'criteria': criteria
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def load_preset_screen(request, preset_name):
    """Load a preset screening configuration"""
    from .screener_service import StockScreenerService
    
    presets = StockScreenerService.get_preset_screens()
    preset = presets.get(preset_name)
    
    if not preset:
        return JsonResponse({'success': False, 'error': 'Preset not found'})
    
    # Run the preset screen
    results = StockScreenerService.screen_stocks(preset['criteria'])
    
    return JsonResponse({
        'success': True,
        'preset': preset,
        'results': results,
        'count': len(results)
    })


@login_required
def save_screener_template(request):
    """Save custom screener configuration"""
    if request.method == 'POST':
        from .models import StockScreenerTemplate
        import json
        
        try:
            data = json.loads(request.body)
            name = data.get('name')
            filters = data.get('filters', {})
            is_public = data.get('is_public', False)
            
            template = StockScreenerTemplate.objects.create(
                user=request.user,
                name=name,
                filters=filters,
                is_public=is_public
            )
            
            return JsonResponse({
                'success': True,
                'template_id': template.id,
                'message': 'Screener template saved successfully!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def my_screener_templates(request):
    """Get user's saved screener templates"""
    from .models import StockScreenerTemplate
    
    templates = StockScreenerTemplate.objects.filter(user=request.user)
    
    templates_data = [{
        'id': t.id,
        'name': t.name,
        'filters': t.filters,
        'is_public': t.is_public,
        'created_at': t.created_at.strftime('%Y-%m-%d %H:%M')
    } for t in templates]
    
    return JsonResponse({
        'success': True,
        'templates': templates_data
    })
