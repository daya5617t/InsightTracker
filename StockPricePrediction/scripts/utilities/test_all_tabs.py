"""
Test script to verify all main tabs/views are working
Run from Django project root: python manage.py shell < scripts/utilities/test_all_tabs.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockPricePrediction.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware

def test_all_views():
    """Test all main views to ensure they render without errors"""
    
    client = Client()
    factory = RequestFactory()
    
    # Get or create test user
    try:
        user = User.objects.get(username='manoj')
    except User.DoesNotExist:
        print("❌ User 'manoj' not found. Please login first.")
        return
    
    print("="*60)
    print("🧪 Testing All Application Tabs/Views")
    print("="*60)
    print()
    
    # Login the client
    client.force_login(user)
    
    # List of views to test (name, url, requires_auth)
    views_to_test = [
        ("Home", "/", False),
        ("Dashboard", "/dashboard/", True),
        ("Portfolio", "/portfolio/", True),
        ("Analytics Map", "/analytics-map/", False),
        ("Alert Settings", "/alerts/settings/", True),
        ("News Feed", "/news/", False),
        ("Compare Stocks", "/compare/", False),
        ("Predict", "/predict/", False),
        ("Browse Stocks", "/all_stocks/", False),
        ("Stock Screener", "/screener/", False),
    ]
    
    results = {"passed": 0, "failed": 0, "errors": []}
    
    for name, url, requires_auth in views_to_test:
        try:
            if requires_auth:
                response = client.get(url, follow=True)
            else:
                response = client.get(url)
            
            if response.status_code == 200:
                print(f"✅ {name:20s} - OK (Status: {response.status_code})")
                results["passed"] += 1
            elif response.status_code == 302:
                print(f"⚠️  {name:20s} - Redirect (Status: {response.status_code})")
                results["passed"] += 1
            else:
                print(f"❌ {name:20s} - Failed (Status: {response.status_code})")
                results["failed"] += 1
                results["errors"].append(f"{name}: Status {response.status_code}")
                
        except Exception as e:
            print(f"💥 {name:20s} - Error: {str(e)[:50]}")
            results["failed"] += 1
            results["errors"].append(f"{name}: {str(e)[:100]}")
    
    print()
    print("="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"✅ Passed: {results['passed']}/{len(views_to_test)}")
    print(f"❌ Failed: {results['failed']}/{len(views_to_test)}")
    
    if results["errors"]:
        print()
        print("🔍 Error Details:")
        for error in results["errors"]:
            print(f"   • {error}")
    else:
        print()
        print("🎉 All tabs are working correctly!")
    
    print("="*60)
    
    # Test API endpoints
    print()
    print("="*60)
    print("🧪 Testing API Endpoints")
    print("="*60)
    print()
    
    api_endpoints = [
        ("Market Status API", "/api/market-status/"),
        ("Market Overview API", "/api/market-overview/"),
        ("Global Markets API", "/api/global-markets/"),
        ("News API", "/api/news/"),
    ]
    
    api_results = {"passed": 0, "failed": 0}
    
    for name, url in api_endpoints:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {name:25s} - OK (Status: {response.status_code})")
                api_results["passed"] += 1
            else:
                print(f"❌ {name:25s} - Failed (Status: {response.status_code})")
                api_results["failed"] += 1
        except Exception as e:
            print(f"💥 {name:25s} - Error: {str(e)[:50]}")
            api_results["failed"] += 1
    
    print()
    print("="*60)
    print(f"API Tests: ✅ {api_results['passed']}/{len(api_endpoints)} passed")
    print("="*60)

if __name__ == "__main__":
    test_all_views()
