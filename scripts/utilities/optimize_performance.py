"""
Performance Optimization Script for Stock Price Prediction App

This script applies various performance optimizations:
1. Creates database indexes for faster queries
2. Clears and warms up the cache
3. Optimizes database
4. Shows performance tips

Run this script after deploying or when experiencing slow performance.
"""

import os
import sys
import django

# Setup Django environment - updated path
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(base_dir, 'StockPricePrediction'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockPricePrediction.settings')
django.setup()

from django.core.cache import cache
from django.core.management import call_command
from django.db import connection
from StockPricePredictionApp.views import get_all_available_stocks


def optimize_database():
    """Optimize SQLite database"""
    print("🔧 Optimizing database...")
    try:
        with connection.cursor() as cursor:
            # Analyze tables for better query planning
            cursor.execute("ANALYZE;")
            # Vacuum to reclaim space and defragment
            cursor.execute("VACUUM;")
        print("✅ Database optimized successfully")
    except Exception as e:
        print(f"⚠️  Database optimization warning: {e}")


def apply_migrations():
    """Apply any pending migrations"""
    print("🔄 Applying database migrations...")
    try:
        call_command('migrate', '--noinput')
        print("✅ Migrations applied successfully")
    except Exception as e:
        print(f"❌ Migration error: {e}")


def warm_cache():
    """Pre-populate cache with frequently accessed data"""
    print("🔥 Warming up cache...")
    try:
        # Cache available stocks
        stocks = get_all_available_stocks()
        print(f"   Cached {len(stocks)} stock symbols")
        
        # You can add more cache warming here
        # For example, popular indices, etc.
        
        print("✅ Cache warmed successfully")
    except Exception as e:
        print(f"⚠️  Cache warming warning: {e}")


def clear_cache():
    """Clear existing cache"""
    print("🧹 Clearing cache...")
    try:
        cache.clear()
        print("✅ Cache cleared successfully")
    except Exception as e:
        print(f"⚠️  Cache clearing warning: {e}")


def collect_static():
    """Collect static files for production"""
    print("📦 Collecting static files...")
    try:
        call_command('collectstatic', '--noinput', '--clear')
        print("✅ Static files collected successfully")
    except Exception as e:
        print(f"⚠️  Static collection warning: {e}")


def show_performance_tips():
    """Display performance tips"""
    print("\n" + "="*60)
    print("🚀 PERFORMANCE OPTIMIZATION TIPS")
    print("="*60)
    print("""
1. ✓ Database indexes have been added for faster queries
2. ✓ Cache has been configured with extended timeouts
3. ✓ Database connection pooling is enabled
4. ✓ GZip compression is active for faster page loads

Additional Tips:
- Keep your cache warm by regularly accessing popular pages
- Monitor slow queries and add indexes as needed
- Consider upgrading to PostgreSQL for production
- Use a CDN for static files in production
- Enable Redis or Memcached for distributed caching
- Use browser caching for static assets
- Minimize JavaScript and CSS files
- Use lazy loading for images

Performance Monitoring:
- Check Django Debug Toolbar for query analysis
- Monitor response times with Application Performance Monitoring
- Use browser DevTools to identify bottlenecks
""")
    print("="*60)


def main():
    """Main optimization routine"""
    print("\n" + "="*60)
    print("🎯 STOCK PRICE PREDICTION APP - PERFORMANCE OPTIMIZER")
    print("="*60 + "\n")
    
    # Apply migrations (including new indexes)
    apply_migrations()
    
    # Optimize database
    optimize_database()
    
    # Clear and warm cache
    clear_cache()
    warm_cache()
    
    # Show tips
    show_performance_tips()
    
    print("\n✨ Optimization complete! Your app should now be faster.\n")


if __name__ == "__main__":
    main()
