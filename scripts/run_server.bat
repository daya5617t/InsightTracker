@echo off
cd /d "%~dp0"
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Running Django migrations...
python manage.py migrate
echo Starting Django development server...
python manage.py runserver
pause

