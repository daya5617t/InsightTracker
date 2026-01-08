# 🚨 Email Alert System - Quick Start Guide

## ✅ System Status: **FULLY OPERATIONAL**

The email alert system has been successfully integrated and is ready to use!

---

## 🎯 Quick Setup (5 Minutes)

### Step 1: Access Alert Settings
1. Start the server (if not running): `python manage.py runserver`
2. Open browser: http://127.0.0.1:8000/
3. Login to your account
4. Navigate to: **http://127.0.0.1:8000/alerts/settings/**

### Step 2: Configure Global Preferences
- **Enable Email Alerts**: Toggle ON
- **Alert Frequency**: Choose "Realtime" (recommended)
- **Quiet Hours**: Set your sleep schedule (e.g., 10:00 PM to 7:00 AM)
- Click **Save Preferences**

### Step 3: Add Stocks to Watchlist
1. Go to Dashboard
2. Search for stocks (e.g., AAPL, TSLA, GOOGL)
3. Click **Add to Watchlist** for each stock

### Step 4: Configure Per-Stock Alerts
1. Return to Alert Settings page
2. For each stock, configure:
   - ✅ **Enable Alert**: ON
   - 📈 **Alert on Rise**: Check if you want alerts when price goes UP
   - 📉 **Alert on Fall**: Check if you want alerts when price goes DOWN
   - 🎯 **Threshold %**: Set trigger percentage (default: 5%)
3. Click **Update** for each stock

---

## 🧪 Test the System

### Send Test Email
1. Go to Alert Settings page
2. Click **Send Test Email** button
3. Check console output for email content (development mode uses console backend)

**Expected Output:**
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: =?utf-8?b?8J+OiSBUZXN0IEFsZXJ0IGZyb20gSW5zaWdodFRyYWNrZXI=?=
From: webmaster@localhost
To: your@email.com
Date: ...

Test alert from InsightTracker
```

### Run Manual Alert Check
```powershell
cd "c:\Users\daya5\Downloads\STOCK TONKS\STOCK TONKS\Stock_Price_Predicton-main\StockPricePrediction"
python manage.py check_stock_alerts
```

**Expected Output:**
```
Starting stock alert check...
Found 3 users with watchlists
Checking alerts for user: yourusername
  Checking AAPL... (threshold: 5.0%)
  Checking TSLA... (threshold: 5.0%)
Alert check completed!
Total alerts sent: 0
```

---

## 📊 How It Works

### Price Monitoring
The system continuously monitors your watchlist stocks and:
1. Fetches current price from Yahoo Finance
2. Compares with last recorded price
3. Calculates percentage change
4. Triggers alert if change exceeds your threshold

### Alert Conditions
You'll receive an email when:
- ✅ Alerts are enabled for that stock
- ✅ Global email alerts are enabled
- ✅ Price change > threshold percentage
- ✅ Alert type matches (rise/fall)
- ✅ Not during quiet hours
- ✅ You haven't been alerted recently (prevents spam)

### Email Content
Each alert includes:
- 🏷️ Stock ticker and company name
- 💰 Old price vs. New price
- 📊 Percentage change with color coding
- 📈/📉 Direction indicator (UP/DOWN)
- ⏰ Timestamp

---

## 🔄 Automated Monitoring Options

### Option 1: Manual Checks (Recommended for Testing)
```powershell
python manage.py check_stock_alerts
```

### Option 2: Windows Task Scheduler (Production)
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Stock Alert Monitor"
4. Trigger: Every 15 minutes during market hours
5. Action: Start a program
   - Program: `python.exe`
   - Arguments: `manage.py check_stock_alerts`
   - Start in: `c:\Users\daya5\Downloads\STOCK TONKS\STOCK TONKS\Stock_Price_Predicton-main\StockPricePrediction`
6. Finish

### Option 3: Continuous Python Script
```python
# Create continuous_monitor.py
import time
import subprocess
import schedule

def check_alerts():
    subprocess.run([
        'python', 'manage.py', 'check_stock_alerts'
    ], cwd=r'c:\Users\daya5\Downloads\STOCK TONKS\STOCK TONKS\Stock_Price_Predicton-main\StockPricePrediction')

# Check every 15 minutes during market hours (9:30 AM - 4:00 PM EST)
schedule.every(15).minutes.do(check_alerts)

while True:
    schedule.run_pending()
    time.sleep(60)
```

Run: `python continuous_monitor.py`

---

## 📧 Configuring Real Email (Gmail)

### Development Mode (Current)
- Emails print to console
- Perfect for testing
- No configuration needed

### Production Mode (Gmail SMTP)

1. **Enable Gmail SMTP in settings.py:**
```python
# Uncomment these lines in StockPricePrediction/settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Not your Gmail password!
DEFAULT_FROM_EMAIL = 'InsightTracker <your-email@gmail.com>'
```

2. **Generate Gmail App Password:**
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification
   - Search for "App passwords"
   - Create password for "Mail"
   - Copy the 16-character password
   - Use this in `EMAIL_HOST_PASSWORD`

3. **Restart Django server** for changes to take effect

---

## 🎨 Alert Settings UI Features

### Dashboard
- **Watchlist Table**: Shows all your stocks with alert status
- **Quick Toggle**: Enable/disable alerts with one click
- **Bulk Actions**: Update multiple stocks at once

### Alert History
- **Recent Alerts**: Last 20 alerts sent
- **Statistics**: Total alerts sent, success rate
- **Filtering**: By stock, date range, alert type

### Testing Tools
- **Test Email**: Send sample alert to verify configuration
- **Dry Run**: Check which stocks would trigger alerts
- **Debug Mode**: Detailed logging for troubleshooting

---

## 🎯 Example Scenarios

### Scenario 1: Day Trader Setup
```
Stock: TSLA
Alert on Rise: ✅ YES
Alert on Fall: ✅ YES
Threshold: 3%
Frequency: Realtime
Quiet Hours: None
```
**Result:** Get alerted on any 3% price movement in TESLA, 24/7

### Scenario 2: Long-Term Investor
```
Stock: AAPL
Alert on Rise: ❌ NO
Alert on Fall: ✅ YES
Threshold: 10%
Frequency: Once per day
Quiet Hours: 10 PM - 7 AM
```
**Result:** Only get alerted if APPLE drops 10%+, max once per day during waking hours

### Scenario 3: Portfolio Monitoring
```
Stocks: Multiple (GOOGL, MSFT, NVDA, META)
Alert on Rise: ✅ YES
Alert on Fall: ✅ YES
Threshold: 5%
Frequency: Realtime
Quiet Hours: Weekends only
```
**Result:** Monitor entire tech portfolio with 5% sensitivity on weekdays

---

## 🐛 Troubleshooting

### No Emails Received
1. Check console output (development mode)
2. Verify user email in Django admin
3. Check spam folder (production mode)
4. Verify SMTP settings (production mode)
5. Test with: **Send Test Email** button

### Alerts Not Triggering
1. Verify alerts enabled globally
2. Check per-stock alert settings
3. Confirm threshold is reasonable
4. Check quiet hours settings
5. Run manual check: `python manage.py check_stock_alerts --ticker AAPL`

### Server Errors
1. Check migrations: `python manage.py showmigrations`
2. Apply missing: `python manage.py migrate`
3. Check logs in console output
4. Verify models.py has alert fields

---

## 📱 Next Steps

1. ✅ **Test the system** with console emails
2. ✅ **Add real stocks** to your watchlist
3. ✅ **Configure alerts** for each stock
4. ✅ **Run manual checks** to see it in action
5. ⏰ **Set up automation** (Task Scheduler recommended)
6. 📧 **Configure Gmail** for real emails (optional)
7. 🎨 **Customize templates** in `alert_service.py`

---

## 📚 Additional Resources

- **Full Documentation**: See `ALERT_SYSTEM_GUIDE.md`
- **API Reference**: Django views in `views.py`
- **Service Logic**: Alert checking in `alert_service.py`
- **Database Models**: Alert schema in `models.py`
- **Management Command**: CLI tool in `management/commands/check_stock_alerts.py`

---

## 🎉 You're All Set!

Your email alert system is fully operational and ready to monitor your stocks 24/7!

**Quick Links:**
- 🏠 Dashboard: http://127.0.0.1:8000/
- ⚙️ Alert Settings: http://127.0.0.1:8000/alerts/settings/
- 📊 Analytics: http://127.0.0.1:8000/analytics/

**Support:** For issues, check the troubleshooting section or review the full documentation.

---

*Last Updated: November 23, 2025*
*System Version: 1.0.0*
*Status: Production Ready ✅*
