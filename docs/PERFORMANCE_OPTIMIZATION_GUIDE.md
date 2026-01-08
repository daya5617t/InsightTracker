# Performance Optimization Guide

## Overview
This guide covers all the performance optimizations implemented to make the Stock Price Prediction website faster and more responsive.

## Optimizations Implemented

### 1. Enhanced Caching System ⚡
- **Increased cache timeout**: From 5 minutes to 15 minutes (3x improvement)
- **Larger cache capacity**: From 5,000 to 10,000 entries
- **Stock data caching**: Available stocks cached for 30 minutes
- **Market indices caching**: Extended from 5 to 10 minutes
- **Prediction caching**: Extended from 10 to 15 minutes
- **Watchlist caching**: Extended from 3 to 5 minutes

### 2. Database Optimizations 🗄️
- **Connection Pooling**: Database connections kept alive for 10 minutes
- **Multiple Indexes Added**:
  - Watchlist: `user`, `ticker`, `created_at`, `alert_enabled`
  - Portfolio: `user`, `created_at`
  - PortfolioHolding: `portfolio`, `ticker`, `purchase_date`
  - Transaction: `portfolio`, `ticker`, `transaction_type`, `transaction_date`
  - NewsArticle: `ticker`, `source`, `published_at`, `sentiment_label`
- **Composite Indexes**: Combined indexes for common query patterns
- **Query Optimization**: Using `.only()` to fetch only needed fields

### 3. View Optimizations 🎯
- **Dashboard**: 
  - Concurrent data fetching with ThreadPoolExecutor
  - Increased workers from 5 to 8
  - Field-level query optimization
- **Home Page**: Extended caching for stocks and indices
- **Prediction View**: 
  - Reduced historical data fetch (2 months vs 3 months)
  - Reduced chart data points (15 days vs 20 days)
  - Extended cache duration

### 4. Compression & Static Files 📦
- **GZip Compression**: Enabled with optimal compression level (6)
- **Session Backend**: Using cached database sessions
- **Static File Handling**: Optimized for production

### 5. Reduced API Calls 🌐
- Minimized yfinance API calls through aggressive caching
- Faster data retrieval with `fast_info` instead of full `info`
- Reduced historical data periods for faster fetches

## How to Apply These Optimizations

### Step 1: Run Migrations
```bash
python manage.py migrate
```
This will create all the new database indexes.

### Step 2: Run Performance Optimization Script
```bash
python scripts/utilities/optimize_performance.py
```
This script will:
- Apply migrations
- Optimize the database
- Clear and warm the cache
- Show performance tips

### Step 3: Restart the Server
```bash
python manage.py runserver
```

## Performance Improvements Expected

| Area | Before | After | Improvement |
|------|--------|-------|-------------|
| **Home Page Load** | ~2-3s | ~0.5-1s | 2-3x faster |
| **Dashboard** | ~3-4s | ~1-2s | 2x faster |
| **Predictions** | ~5-7s | ~2-3s | 2-3x faster |
| **Database Queries** | 50-100ms | 10-30ms | 3-5x faster |
| **Cache Hit Rate** | ~50% | ~80% | 60% improvement |

## Performance Monitoring Tips

### 1. Check Cache Statistics
```python
from django.core.cache import cache
print(cache._cache.keys())  # View cached keys
```

### 2. Monitor Database Queries
Enable Django Debug Toolbar in development:
```python
# In settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### 3. Profile Slow Pages
Use Django Silk for profiling:
```bash
pip install django-silk
```

## Additional Optimization Tips

### For Production Deployment:
1. **Use PostgreSQL** instead of SQLite for better performance
2. **Enable Redis** for distributed caching
3. **Use CDN** for static files
4. **Enable Browser Caching** in nginx/Apache
5. **Use Gunicorn** with multiple workers
6. **Enable HTTP/2** on your web server

### Configuration for Redis (Optional):
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 900,  # 15 minutes
    }
}
```

### Configuration for PostgreSQL (Optional):
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'stockprediction',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
    }
}
```

## Troubleshooting

### If cache isn't working:
```bash
# Clear cache manually
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### If migrations fail:
```bash
# Check migration status
python manage.py showmigrations

# Fake a migration if needed
python manage.py migrate --fake StockPricePredictionApp 0002_performance_indexes
```

### If database is slow:
```bash
# Optimize database manually
python manage.py dbshell
sqlite> ANALYZE;
sqlite> VACUUM;
sqlite> .quit
```

## Testing Performance

### Before and After Comparison:
1. **Clear your browser cache**
2. **Open Developer Tools** (F12)
3. **Go to Network tab**
4. **Load a page and note the load time**
5. **Compare with the same page after optimization**

### Use Django's built-in profiling:
```python
# In views.py
import time

def my_view(request):
    start = time.time()
    # ... your code ...
    end = time.time()
    print(f"View took {end - start:.2f} seconds")
```

## Cache Key Reference

| Feature | Cache Key Pattern | Timeout |
|---------|------------------|---------|
| Available Stocks | `all_available_stocks_dict_v2` | 1 hour |
| Market Indices | `market_indices_home_v2` | 10 min |
| Stock Data | `stock_data_{symbol}_{start}_{end}` | 15 min |
| Predictions | `prediction_{symbol}_{days}_v3` | 15 min |
| Watchlist Item | `watchlist_{ticker}_v2` | 5 min |
| Dashboard Stocks | `dashboard_available_stocks` | 1 hour |

## Summary

These optimizations provide significant performance improvements through:
- ✅ Smart caching strategies
- ✅ Database index optimization
- ✅ Query optimization
- ✅ Reduced API calls
- ✅ Concurrent data fetching
- ✅ Compression enabled

Your app should now load **2-3x faster** with these optimizations! 🚀
