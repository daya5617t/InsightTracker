# Project Structure Documentation

## 📁 Directory Organization

```
InsightTracker/
│
├── 📁 StockPricePrediction/          # Django Web Application
│   ├── 📁 StockPricePrediction/      # Main Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py               # Django configuration
│   │   ├── urls.py                   # Main URL routing
│   │   ├── wsgi.py                   # WSGI configuration
│   │   └── asgi.py                   # ASGI configuration
│   │
│   ├── 📁 StockPricePredictionApp/   # Main Django application
│   │   ├── models.py                 # Database models
│   │   ├── views.py                  # View functions
│   │   ├── urls.py                   # App URL routing
│   │   ├── admin.py                  # Admin interface
│   │   ├── ml_service.py             # ML integration service
│   │   ├── utils.py                  # Utility functions
│   │   ├── 📁 templates/             # HTML templates
│   │   ├── 📁 migrations/            # Database migrations
│   │   ├── 📁 management/            # Custom management commands
│   │   └── 📁 data/                  # App-specific data (if needed)
│   │
│   ├── 📁 static/                    # Static files (CSS, JS, images)
│   │   ├── 📁 assets/
│   │   │   ├── 📁 css/              # Stylesheets
│   │   │   ├── 📁 js/               # JavaScript files
│   │   │   ├── 📁 images/           # Image assets
│   │   │   ├── 📁 libs/             # Third-party libraries
│   │   │   └── 📁 vendor/           # Vendor assets
│   │   └── 📁 contact/              # Contact page assets
│   │
│   └── manage.py                     # Django management script
│
├── 📁 data/                          # Data Storage
│   ├── 📁 datasets/                  # CSV and data files
│   │   ├── all_stocks.csv
│   │   ├── AAPL_historical.csv
│   │   ├── MSFT_historical.csv
│   │   └── ... (other stock data)
│   │
│   ├── 📁 models/                    # Trained ML models
│   │   ├── lstm_model.h5
│   │   ├── best_weights.weights.h5
│   │   └── ... (model checkpoints)
│   │
│   └── 📁 database/                  # Database files
│       └── db.sqlite3
│
├── 📁 scripts/                       # Utility Scripts
│   ├── start.bat                     # Windows startup script
│   ├── start.sh                      # Linux/Mac startup script
│   ├── run_server.bat               # Windows server script
│   ├── run_server.ps1               # PowerShell server script
│   │
│   └── 📁 utilities/                 # Utility scripts
│       ├── clear_cache.py
│       ├── create_watchlist_table.py
│       ├── test_prediction.py
│       └── train_model.py
│
├── 📁 docs/                          # Documentation
│   ├── README_original.md           # Original project README
│   ├── implementation_plan.md        # Implementation roadmap
│   ├── PERFORMANCE_OPTIMIZATIONS.md # Performance guide
│   ├── UI_CHANGES.md                # UI modification guide
│   ├── VS_CODE_SETUP.md             # Development setup
│   ├── LIVE_UPDATES_IMPLEMENTATION.md # Live updates guide
│   ├── FUTURE_IMPLEMENTATIONS.md    # Future features
│   ├── OPTIMIZATION_SUMMARY.md      # Optimization summary
│   └── walkthrough.md               # User walkthrough
│
├── 📁 config/                        # Configuration Files
│   └── ml_config.py                 # ML model configuration
│
├── 📁 venv/                          # Python Virtual Environment
│   └── ... (virtual environment files)
│
├── README.md                         # Main project README
├── requirements.txt                  # Python dependencies
├── .gitignore                       # Git ignore rules
├── .env.example                     # Environment variables example
├── Stock_Price_Prediction.ipynb     # Jupyter notebook for analysis
└── LICENSE                          # Project license
```

## 📋 File Descriptions

### Core Django Files
- **manage.py**: Django's command-line utility for administrative tasks
- **settings.py**: Django project configuration and settings
- **urls.py**: URL routing and endpoint definitions
- **models.py**: Database model definitions
- **views.py**: View functions handling HTTP requests

### Data Organization
- **datasets/**: All CSV files and historical stock data
- **models/**: Trained ML models and model weights
- **database/**: SQLite database files

### Scripts & Utilities
- **start.bat/start.sh**: One-click startup scripts
- **utilities/**: Helper scripts for maintenance and training
- **run_server.***: Server launching scripts

### Documentation
- **docs/**: Comprehensive project documentation
- **README.md**: Main project overview and setup guide
- **.env.example**: Environment configuration template

### Static Assets
- **css/**: Stylesheets including dark theme
- **js/**: JavaScript for interactivity
- **images/**: Static images and icons
- **vendor/**: Third-party assets

## 🎯 Benefits of This Structure

### ✅ Organized & Clean
- Clear separation of concerns
- Easy to navigate and understand
- Professional project layout

### ✅ Scalable
- Easy to add new features
- Modular design for team collaboration
- Clear data and code separation

### ✅ Maintainable
- Documentation is centralized
- Scripts are organized by purpose
- Configuration is externalized

### ✅ Professional
- Follows Django best practices
- Industry-standard directory structure
- Version control friendly

## 🚀 Quick Navigation

- **Need to modify UI?** → `StockPricePrediction/static/assets/`
- **Database changes?** → `StockPricePredictionApp/models.py` & `migrations/`
- **Add new features?** → `StockPricePredictionApp/views.py` & `templates/`
- **ML model work?** → `data/models/` & `scripts/utilities/`
- **Documentation?** → `docs/`
- **Configuration?** → `config/` & `.env`