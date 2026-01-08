"""
Offline fallback sample data used when live market/news APIs are not reachable.
"""

from datetime import datetime, timedelta
import math


def _generate_dates(days):
    today = datetime.utcnow().date()
    return [(today - timedelta(days=days - idx)).strftime("%Y-%m-%d") for idx in range(days)]


_BASE_DATES = _generate_dates(30)

_SAMPLE_STOCK_HISTORY = {
    "AAPL": [
        {"Date": d, "Open": 180 + idx * 0.3, "High": 181 + idx * 0.35,
         "Low": 179 + idx * 0.25, "Close": 180.2 + idx * 0.32,
         "Volume": 72_000_000 + idx * 150_000}
        for idx, d in enumerate(_BASE_DATES)
    ],
    "MSFT": [
        {"Date": d, "Open": 320 + idx * 0.4, "High": 321 + idx * 0.45,
         "Low": 319 + idx * 0.35, "Close": 320.5 + idx * 0.38,
         "Volume": 28_000_000 + idx * 120_000}
        for idx, d in enumerate(_BASE_DATES)
    ],
    "TSLA": [
        {"Date": d, "Open": 250 + math.sin(idx / 3) * 4,
         "High": 253 + math.sin(idx / 3) * 4.5,
         "Low": 247 + math.sin(idx / 3) * 3.5,
         "Close": 251 + math.sin(idx / 3) * 4.2,
         "Volume": 35_000_000 + idx * 180_000}
        for idx, d in enumerate(_BASE_DATES)
    ],
    "GOOGL": [
        {"Date": d, "Open": 135 + idx * 0.25,
         "High": 136 + idx * 0.3,
         "Low": 134 + idx * 0.2,
         "Close": 135.4 + idx * 0.27,
         "Volume": 18_000_000 + idx * 110_000}
        for idx, d in enumerate(_BASE_DATES)
    ],
}


_SAMPLE_NEWS = [
    {
        "title": "Global Markets Edge Higher Amid Tech Rally",
        "link": "https://example.com/news/markets-tech-rally",
        "published": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "published_date": datetime.utcnow(),
        "summary": "Technology and consumer discretionary stocks lifted global indices as investors digested earnings.",
        "source": "Sample Wire",
        "publisher": "Sample Wire",
        "related_ticker": "AAPL",
    },
    {
        "title": "Central Bank Signals Patience On Further Rate Moves",
        "link": "https://example.com/news/central-bank-outlook",
        "published": (datetime.utcnow() - timedelta(hours=2)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "published_date": datetime.utcnow() - timedelta(hours=2),
        "summary": "Officials highlighted moderating inflation trends while emphasising data-dependent decisions.",
        "source": "Sample Wire",
        "publisher": "Sample Wire",
        "related_ticker": "MSFT",
    },
    {
        "title": "Energy Shares Gain As Oil Holds Near Recent Highs",
        "link": "https://example.com/news/energy-oil-prices",
        "published": (datetime.utcnow() - timedelta(hours=5)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "published_date": datetime.utcnow() - timedelta(hours=5),
        "summary": "Crude oil prices stabilised after recent gains, supporting major integrated producers.",
        "source": "Sample Wire",
        "publisher": "Sample Wire",
        "related_ticker": "XOM",
    },
]


_SAMPLE_BROWSE_STOCKS = [
    {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "close": 188.45,
        "net_change": 1.35,
        "percent_change": 0.72,
        "high": 189.10,
        "low": 186.90,
        "volume": 72_540_000,
    },
    {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "close": 331.28,
        "net_change": -0.85,
        "percent_change": -0.26,
        "high": 333.00,
        "low": 329.45,
        "volume": 28_320_000,
    },
    {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "close": 254.12,
        "net_change": 3.95,
        "percent_change": 1.58,
        "high": 256.40,
        "low": 248.70,
        "volume": 35_890_000,
    },
    {
        "symbol": "GOOGL",
        "name": "Alphabet Inc. Class A",
        "close": 138.67,
        "net_change": 0.64,
        "percent_change": 0.46,
        "high": 139.20,
        "low": 136.95,
        "volume": 18_450_000,
    },
    {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "close": 451.20,
        "net_change": 5.40,
        "percent_change": 1.21,
        "high": 454.00,
        "low": 444.10,
        "volume": 24_980_000,
    },
]


def get_sample_news():
    """Return offline fallback news stories."""
    return _SAMPLE_NEWS


def get_sample_stock_history(symbol):
    """Return offline fallback OHLCV history for the given ticker."""
    return _SAMPLE_STOCK_HISTORY.get(symbol.upper())


def get_default_sample_symbols():
    return "AAPL", "MSFT"


def get_sample_prediction(symbol, days):
    """Generate a synthetic prediction curve for the symbol."""
    base_symbol = symbol.upper() if symbol and symbol.upper() in _SAMPLE_STOCK_HISTORY else "AAPL"
    start_price = _SAMPLE_STOCK_HISTORY[base_symbol][-1]["Close"]
    predictions = []
    for i in range(1, days + 1):
        # Use a gentle sinusoidal wave around the start price
        val = start_price * (1 + 0.002 * i + 0.01 * math.sin(i / 3))
        predictions.append(((datetime.utcnow() + timedelta(days=i)).strftime("%Y-%m-%d"), round(val, 2)))
    return predictions


def get_sample_browse_stocks():
    return _SAMPLE_BROWSE_STOCKS

