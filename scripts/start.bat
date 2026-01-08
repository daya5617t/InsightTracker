@echo off
REM InsightTracker Startup Script for Windows

echo 🚀 Starting InsightTracker...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Run migrations
echo 🗄️ Running database migrations...
cd StockPricePrediction
python manage.py makemigrations
python manage.py migrate

REM Create superuser if needed
echo 👤 Setting up admin user...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').exists() else print('Admin user already exists') | python manage.py shell

REM Start the server
echo 🌐 Starting development server...
echo 🔗 Open your browser to: http://127.0.0.1:8000
echo 🔗 Admin panel: http://127.0.0.1:8000/admin (admin/admin)
echo.
python manage.py runserver

pause