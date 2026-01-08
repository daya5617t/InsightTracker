@echo off
echo 🚀 InsightTracker Deployment Script (Windows)
echo =============================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install production dependencies
echo.
echo Installing production dependencies...
pip install gunicorn whitenoise python-dotenv psycopg2-binary

REM Generate secret key
echo.
echo Generating Django secret key...
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))" > temp_secret.txt
set /p SECRET_KEY=<temp_secret.txt
del temp_secret.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo.
    echo Creating .env file...
    (
        echo %SECRET_KEY%
        echo DEBUG=False
        echo ALLOWED_HOSTS=localhost,127.0.0.1
    ) > .env
    echo [SUCCESS] .env file created
) else (
    echo [WARNING] .env file already exists
)

REM Collect static files
echo.
echo Collecting static files...
cd StockPricePrediction
python manage.py collectstatic --noinput
echo [SUCCESS] Static files collected

REM Run migrations
echo.
echo Running database migrations...
python manage.py migrate
echo [SUCCESS] Migrations completed
cd ..

REM Git setup
echo.
echo Setting up Git...
if not exist ".git\" (
    git init
    git branch -M main
    echo [SUCCESS] Git initialized
)

git add .
git commit -m "Prepare for deployment"
echo [SUCCESS] Git commit completed

echo.
echo =============================================
echo ✅ Deployment preparation complete!
echo.
echo Next steps:
echo 1. Push to GitHub:
echo    git remote add origin https://github.com/yourusername/insighttracker.git
echo    git push -u origin main
echo.
echo 2. Deploy to platform of choice:
echo    - Render: Connect GitHub repo at render.com
echo    - Railway: Run 'railway init && railway up'
echo    - PythonAnywhere: Upload and configure
echo.
echo Check your .env file for the SECRET_KEY
pause
