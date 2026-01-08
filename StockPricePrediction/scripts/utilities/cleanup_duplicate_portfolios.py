"""
Cleanup script to remove duplicate Portfolio entries
Run this from the Django project root:
python manage.py shell < scripts/utilities/cleanup_duplicate_portfolios.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockPricePrediction.settings')
django.setup()

from django.contrib.auth.models import User
from StockPricePredictionApp.models import Portfolio

def cleanup_duplicate_portfolios():
    """Remove duplicate portfolios for each user, keeping only the first one"""
    
    print("🔍 Scanning for duplicate portfolios...")
    
    users_with_duplicates = []
    total_removed = 0
    
    for user in User.objects.all():
        # Get all "My Portfolio" entries for this user
        portfolios = Portfolio.objects.filter(user=user, name="My Portfolio").order_by('created_at')
        
        if portfolios.count() > 1:
            users_with_duplicates.append(user.username)
            
            # Keep the first one, delete the rest
            first_portfolio = portfolios.first()
            duplicates = portfolios.exclude(id=first_portfolio.id)
            
            count = duplicates.count()
            print(f"   User: {user.username} - Found {count} duplicate(s)")
            
            # Delete duplicates
            duplicates.delete()
            total_removed += count
            
            print(f"   ✓ Kept portfolio ID: {first_portfolio.id}, removed {count} duplicate(s)")
    
    print("\n" + "="*50)
    if users_with_duplicates:
        print(f"✅ Cleanup complete!")
        print(f"   Users affected: {len(users_with_duplicates)}")
        print(f"   Total duplicates removed: {total_removed}")
        print(f"   Users: {', '.join(users_with_duplicates)}")
    else:
        print("✅ No duplicate portfolios found!")
    print("="*50)

if __name__ == "__main__":
    cleanup_duplicate_portfolios()
