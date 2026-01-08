#!/bin/bash
# InsightTracker Startup Script

echo "🚀 Starting InsightTracker..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
cd StockPricePrediction
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("Admin user created: admin/admin")
else:
    print("Admin user already exists")
EOF

# Start the server
echo "🌐 Starting development server..."
echo "🔗 Open your browser to: http://127.0.0.1:8000"
echo "🔗 Admin panel: http://127.0.0.1:8000/admin (admin/admin)"
echo ""
python manage.py runserver