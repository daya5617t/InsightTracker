# PowerShell script to run the Django server
Set-Location $PSScriptRoot
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1
Write-Host "Running Django migrations..." -ForegroundColor Green
python manage.py migrate
Write-Host "Starting Django development server..." -ForegroundColor Green
python manage.py runserver

