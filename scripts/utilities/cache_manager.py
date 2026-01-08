"""
Quick Cache Management Script

Use this to clear or warm the cache when needed.
"""

import os
import sys
import django

# Setup Django environment
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(base_dir, 'StockPricePrediction'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockPricePrediction.settings')
django.setup()

from django.core.cache import cache
from StockPricePredictionApp.views import get_all_available_stocks


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage application cache')
    parser.add_argument('action', choices=['clear', 'warm', 'info'], 
                       help='Action to perform: clear, warm, or info')
    
    args = parser.parse_args()
    
    if args.action == 'clear':
        print("🧹 Clearing cache...")
        cache.clear()
        print("✅ Cache cleared successfully!")
        
    elif args.action == 'warm':
        print("🔥 Warming cache...")
        stocks = get_all_available_stocks()
        print(f"✅ Cache warmed with {len(stocks)} stock symbols")
        
    elif args.action == 'info':
        print("ℹ️  Cache Information:")
        print(f"   Backend: {cache.__class__.__name__}")
        print("   Available stocks cached: ", end="")
        if cache.get('all_available_stocks_dict_v2'):
            print("Yes ✓")
        else:
            print("No ✗")


if __name__ == "__main__":
    main()
