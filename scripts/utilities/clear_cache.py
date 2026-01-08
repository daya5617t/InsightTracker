import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockPricePrediction.settings')
django.setup()

from django.core.cache import cache

# Clear all cache
cache.clear()
print("✅ Cache cleared successfully!")
print("Now visit http://127.0.0.1:8000/analytics/ again")
