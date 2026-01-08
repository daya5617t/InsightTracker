# 📈 InsightTracker - AI Stock Price Prediction Platform

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Advanced AI-powered stock analysis, predictions, and market insights to help you make informed investment decisions.**

## 🚀 Features

- 🤖 **AI-Powered Predictions**: LSTM neural networks for accurate stock price forecasting
- 📊 **Real-time Analytics**: Live market data and interactive charts
- 🎯 **Market Insights**: Comprehensive analysis and comparison tools
- 📰 **News Integration**: Latest financial news and market updates
- 🌙 **Modern Dark UI**: Professional, responsive dark theme interface
- 📱 **Mobile Responsive**: Works seamlessly across all devices

## 🏗️ Project Structure

```
InsightTracker/
├── 📁 StockPricePrediction/          # Django web application
│   ├── 📁 StockPricePrediction/      # Main Django project
│   ├── 📁 StockPricePredictionApp/   # Main application
│   ├── 📁 static/                    # CSS, JS, assets
│   └── 📁 templates/                 # HTML templates
├── 📁 data/                          # Data files and models
│   ├── 📁 datasets/                  # CSV data files
│   ├── 📁 models/                    # Trained ML models
│   └── 📁 database/                  # Database files
├── 📁 scripts/                       # Utility scripts
│   └── 📁 utilities/                 # Helper scripts
├── 📁 docs/                          # Documentation
└── 📁 config/                        # Configuration files
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd InsightTracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   cd StockPricePrediction
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Open your browser** and navigate to `http://127.0.0.1:8000`

## 📊 Usage

1. **Dashboard**: View your portfolio overview and market statistics
2. **Analytics**: Explore detailed stock analysis and charts
3. **Predictions**: Get AI-powered price forecasts
4. **Compare**: Compare multiple stocks side by side
5. **News**: Stay updated with latest market news
6. **Browse**: Search and discover new investment opportunities

## 🔧 Configuration

- **Database**: SQLite (default) - configured in `settings.py`
- **Static Files**: Served from `/static/` directory
- **Media Files**: User uploads stored in `/media/`
- **Environment Variables**: Configure in `.env` file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Documentation

- [📖 Full Documentation](docs/README_original.md)
- [🚀 Implementation Plan](docs/implementation_plan.md)
- [⚡ Performance Optimizations](docs/PERFORMANCE_OPTIMIZATIONS.md)
- [🎨 UI Changes](docs/UI_CHANGES.md)
- [🔧 VS Code Setup](docs/VS_CODE_SETUP.md)
- [📡 Live Updates](docs/LIVE_UPDATES_IMPLEMENTATION.md)
- [🚀 Future Implementations](docs/FUTURE_IMPLEMENTATIONS.md)
- [⚙️ Walkthrough Guide](docs/walkthrough.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- TensorFlow team for the ML framework
- Django community for the web framework
- Yahoo Finance for market data
- Chart.js for beautiful visualizations

---

**Built with ❤️ for smarter investing**