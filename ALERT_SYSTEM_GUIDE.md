# 📧 Stock Price Alert System - Complete Guide

## 🚀 Features Implemented

### ✅ What's New:
1. **Automatic Price Monitoring** - Tracks all watchlist stocks continuously
2. **Email Alerts** - Beautiful HTML emails when prices move significantly  
3. **Customizable Thresholds** - Set custom % change triggers per stock
4. **Quiet Hours** - Don't get alerts while sleeping
5. **Alert History** - Track all past alerts
6. **Test Email** - Verify your email setup instantly

---

## 📋 Setup Instructions

### Step 1: Run Database Migrations

```powershell
cd "c:\Users\daya5\Downloads\STOCK TONKS\STOCK TONKS\Stock_Price_Predicton-main\StockPricePrediction"
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Configure Email (Choose One)

#### Option A: Console Backend (Development/Testing)
**Already configured!** Emails print to your terminal/console.

#### Option B: Gmail SMTP (Production)
Edit `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-gmail-app-password'
DEFAULT_FROM_EMAIL = 'InsightTracker <your-email@gmail.com>'
```

**Getting Gmail App Password:**
1. Go to Google Account → Security
2. Enable 2-Factor Authentication
3. Generate App Password for "Mail"
4. Use that 16-character password (not your regular password)

---

## 🎯 How to Use

### For Users:

1. **Add Stocks to Watchlist**
   - Browse stocks and click "Add to Watchlist"
   - Or go to Dashboard → Watchlist

2. **Configure Alerts**
   - Go to: `http://127.0.0.1:8000/alerts/settings/`
   - Enable/disable email alerts globally
   - Set quiet hours (e.g., 10 PM - 8 AM)
   - Customize alert threshold for each stock

3. **Test Email System**
   - Click "Send Test Email" button
   - Check your email/console

---

## ⚙️ Running the Alert System

### Manual Check (Test It Now):

```powershell
python manage.py check_stock_alerts
```

### Check Specific Stock:

```powershell
python manage.py check_stock_alerts --ticker AAPL
```

### Automated Monitoring (Schedule It):

#### Option 1: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Every 15 minutes (or your preference)
4. Action: Start a program
   - Program: `python`
   - Arguments: `manage.py check_stock_alerts`
   - Start in: `c:\Users\daya5\Downloads\STOCK TONKS\STOCK TONKS\Stock_Price_Predicton-main\StockPricePrediction`

#### Option 2: Python Script (Keep Running)
Create `run_alerts_continuous.py`:

```python
import time
import os
import subprocess

while True:
    print("Checking stock alerts...")
    subprocess.call(['python', 'manage.py', 'check_stock_alerts'])
    print("Sleeping for 15 minutes...")
    time.sleep(900)  # 15 minutes = 900 seconds
```

Run it:
```powershell
python run_alerts_continuous.py
```

---

## 📊 Alert System Logic

### When Does an Alert Trigger?

1. **Price Change Threshold Met:**
   - Stock rises >= threshold % (default 5%) → Rise alert
   - Stock falls >= threshold % (default 5%) → Fall alert

2. **Alert Conditions:**
   - User has email alerts enabled globally
   - Specific stock has alerts enabled
   - Alert type is enabled (rise/fall)
   - Not during quiet hours
   - Price hasn't been checked yet OR price changed since last check

3. **After Alert Sent:**
   - Last price is updated to current price
   - Alert logged to database
   - Email sent to user

### Example:
- Last price: $100
- Threshold: 5%
- Current price: $106
- Change: +6%
- **Result:** Alert triggered! ✉️

---

## 🎨 Email Preview

Users receive beautiful HTML emails with:
- Stock symbol and emoji (🚀 for rise, 📉 for fall)
- Old price → New price comparison
- Change percentage highlighted
- Direct link to stock details
- Timestamp of alert
- Professional gradient design

---

## 🔧 Customization Options

### Per-Stock Settings:
- **Alert Enabled:** On/Off toggle
- **Alert on Rise:** Get notified on price increases
- **Alert on Fall:** Get notified on price drops
- **Threshold:** Custom % change (e.g., 3%, 10%, 15%)

### Global Settings:
- **Email Alerts:** Master on/off switch
- **Alert Frequency:**
  - Realtime: Instant emails
  - Hourly: One digest per hour
  - Daily: One digest per day
- **Quiet Hours:** Set sleep schedule

---

## 📁 Files Created/Modified

### New Files:
```
StockPricePredictionApp/
├── models.py (UPDATED)
├── alert_service.py (NEW)
├── alert_views.py (NEW)
├── management/
│   └── commands/
│       └── check_stock_alerts.py (NEW)
└── templates/
    └── template/
        └── alert_settings.html (NEW)
```

### Modified Files:
```
- urls.py (added alert routes)
- views.py (imported alert views)
- settings.py (added email config)
```

---

## 🐛 Troubleshooting

### Emails Not Sending?

**Check 1: Email Backend**
```python
# In settings.py
print(EMAIL_BACKEND)  # Should print correct backend
```

**Check 2: User Email**
- User must have valid email in account
- Check: Django Admin → Users → [Your User] → Email

**Check 3: Console Output**
- If using console backend, emails print in terminal
- Look for email content in command output

**Check 4: Gmail Blockingg?**
- Use App Password, not regular password
- Enable "Less secure app access" (deprecated)
- Check Gmail "Blocked sign-in attempt" notifications

### No Alerts Triggering?

**Check 1: Watchlist Setup**
```python
# In Django shell:
python manage.py shell
>>> from StockPricePredictionApp.models import Watchlist
>>> Watchlist.objects.filter(alert_enabled=True).count()
# Should be > 0
```

**Check 2: Price Threshold**
- Default 5% might be too high
- Lower to 1-2% for more frequent alerts

**Check 3: Quiet Hours**
- Make sure current time isn't in quiet hours range

### Management Command Not Found?

```powershell
# Ensure __init__.py exists:
New-Item "StockPricePredictionApp/management/__init__.py" -ItemType File
New-Item "StockPricePredictionApp/management/commands/__init__.py" -ItemType File
```

---

## 💡 Tips & Best Practices

1. **Start with Test Email**
   - Always test before relying on alerts
   - Verify emails arrive in inbox (not spam)

2. **Reasonable Thresholds**
   - 5-10% for long-term holds
   - 1-3% for day trading
   - 10-15% for volatile stocks

3. **Quiet Hours**
   - Set to your sleep schedule
   - Prevents notification overload at night

4. **Check Frequency**
   - Every 15 minutes: Good balance
   - Every 5 minutes: Real-time (more load)
   - Every hour: Relaxed monitoring

5. **Email Quotas**
   - Gmail: 500 emails/day limit
   - Add multiple users carefully
   - Consider paid email service for scale

---

## 🚀 Next Steps

### Phase 1: Testing ✅
- Run migrations
- Test with console backend
- Send test emails
- Check alerts manually

### Phase 2: Production
- Configure Gmail SMTP
- Schedule automated checks
- Monitor for 24 hours
- Adjust thresholds

### Phase 3: Scale
- Add SMS alerts (Twilio)
- Add browser notifications
- Add Telegram/Discord bots
- Build mobile app

---

## 📞 Support

Need help? Check:
1. Django server logs
2. Email in console/terminal
3. Alert history in settings page
4. Database for PriceAlert records

---

## 🎉 Success!

You now have a **fully automated stock price alert system** that:
- ✅ Monitors your watchlist 24/7
- ✅ Sends beautiful email alerts
- ✅ Respects your preferences
- ✅ Tracks alert history
- ✅ Completely customizable

**Start receiving alerts in minutes!** 🚀
