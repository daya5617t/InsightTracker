# VS Code Setup Guide for Stock Price Prediction Project

## Prerequisites
- Python 3.10 or higher
- VS Code installed
- Virtual environment already set up (venv folder exists)

## Quick Start

### Option 1: Using VS Code Debugger (Recommended)
1. Open the project folder in VS Code
2. Press `F5` or go to Run > Start Debugging
3. Select "Python: Django" configuration
4. The server will start on http://127.0.0.1:8000

### Option 2: Using Terminal in VS Code
1. Open the integrated terminal in VS Code (Ctrl+`)
2. Navigate to the project directory:
   ```powershell
   cd StockPricePrediction
   ```
3. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
4. Run the server:
   ```powershell
   python manage.py runserver
   ```

### Option 3: Using Run Scripts
- **Windows PowerShell**: Run `.\run_server.ps1`
- **Windows Command Prompt**: Run `run_server.bat`

## Dependencies

All dependencies are already installed in the virtual environment. If you need to reinstall:

```powershell
cd StockPricePrediction
.\venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
```

## Project Structure

```
Stock_Price_Predicton-main/
├── StockPricePrediction/        # Main Django project
│   ├── manage.py                # Django management script
│   ├── StockPricePrediction/    # Project settings
│   │   └── settings.py          # Django settings
│   └── StockPricePredictionApp/ # Main application
│       ├── views.py             # View functions
│       ├── urls.py              # URL routing
│       └── templates/           # HTML templates
├── requirements.txt             # Python dependencies
└── .vscode/                     # VS Code configuration
    ├── launch.json              # Debug configuration
    └── settings.json            # VS Code settings
```

## Running the Server

The server will be available at:
- **Local**: http://127.0.0.1:8000
- **Network**: http://0.0.0.0:8000

## Troubleshooting

### Port Already in Use
If port 8000 is already in use:
```powershell
python manage.py runserver 8001
```

### Virtual Environment Not Activated
Make sure the virtual environment is activated. You should see `(venv)` in your terminal prompt.

### Dependencies Not Found
Reinstall dependencies:
```powershell
pip install -r ..\requirements.txt
```

### Database Issues
Run migrations:
```powershell
python manage.py migrate
```

## Features

- Stock price visualization
- Stock comparison
- Price prediction using LSTM
- Live price updates
- Market news feed
- Analytics map
- All stocks table

## VS Code Extensions (Recommended)

- Python (Microsoft)
- Django (Baptiste Darthenay)
- Python Docstring Generator
- Python Test Explorer

## Debugging

1. Set breakpoints in your Python files
2. Press `F5` to start debugging
3. Use the debug toolbar to step through code
4. Check the Debug Console for output

## Notes

- The project uses Django 5.2.8
- TensorFlow is used for LSTM predictions
- yfinance is used for stock data
- All data is fetched from Yahoo Finance API

