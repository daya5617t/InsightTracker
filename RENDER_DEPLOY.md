# Deploy to Render

## Important Note About Netlify vs Render

**Netlify DOES NOT support Django apps!** Netlify is for static sites (React, Vue, Next.js, etc.).

Your Django app is correctly configured for **Render**, which supports Python/Django applications.

## Quick Deploy to Render

### Step 1: Push to GitHub (Already Done ✅)
Your code is already at: https://github.com/daya5617t/InsightTracker.git

### Step 2: Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `daya5617t/InsightTracker`
4. Configure the service:
   - **Name**: `insighttracker` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `cd StockPricePrediction && gunicorn StockPricePrediction.wsgi:application --bind 0.0.0.0:$PORT`

### Step 3: Environment Variables

Add these in Render Dashboard → Environment → Environment Variables:

```
SECRET_KEY = (Click "Generate" button in Render)
DEBUG = False
DJANGO_SETTINGS_MODULE = StockPricePrediction.settings_production
PYTHON_VERSION = 3.11.4
ALLOWED_HOSTS = .onrender.com
WEB_CONCURRENCY = 2
```

Optional (for news/stock APIs):
```
NEWS_API_KEY = your_newsapi_key
ALPHA_VANTAGE_API_KEY = your_alphavantage_key
FMP_API_KEY = your_fmp_key
```

### Step 4: Deploy!

Click **"Create Web Service"** and wait for deployment (5-10 minutes).

## Troubleshooting

### Build Failed?

**Check the build logs** for specific errors:

1. **Permission denied on build.sh**:
   - Fixed by adding `chmod +x build.sh &&` to build command

2. **Python version not found**:
   - Make sure `runtime.txt` has `python-3.11.4`

3. **Module not found**:
   - Check `requirements.txt` has all dependencies
   - Verify build command ran successfully

4. **Static files not loading**:
   - Build command includes `collectstatic`
   - WhiteNoise is configured in settings_production.py

### App Crashes on Start?

1. Check Start Command is correct:
   ```bash
   cd StockPricePrediction && gunicorn StockPricePrediction.wsgi:application --bind 0.0.0.0:$PORT
   ```

2. Verify environment variables are set

3. Check logs: Dashboard → Your Service → Logs

### Database Issues?

SQLite is used by default (included). For production PostgreSQL:

1. Create a PostgreSQL database on Render
2. Copy the **Internal Database URL**
3. Add environment variable:
   ```
   DATABASE_URL = postgresql://...
   ```

## Alternative: Deploy Using render.yaml

If you want automatic deployment from `render.yaml`:

1. Push changes to GitHub
2. In Render Dashboard: **New** → **Blueprint**
3. Select your repo
4. Render will read `render.yaml` and configure everything automatically

## Post-Deployment

### Your app will be at:
```
https://insighttracker.onrender.com
```
(or whatever name you chose)

### Admin Access
Create superuser after deployment:
```bash
# In Render Shell (Dashboard → Shell button)
cd StockPricePrediction
python manage.py createsuperuser
```

## Free Tier Limitations

Render free tier:
- ✅ 750 hours/month
- ⚠️ Spins down after 15 min inactivity (first request takes ~30-60 seconds)
- ✅ Automatic SSL
- ✅ Automatic deploys from GitHub

## Need Help?

1. Check Render logs first
2. Review this guide
3. Check `DEPLOYMENT_GUIDE.md` for more details

## Files Changed for Render Deployment

- ✅ `render.yaml` - Render configuration
- ✅ `build.sh` - Build script with correct paths
- ✅ `runtime.txt` - Python 3.11.4
- ✅ `requirements.txt` - Added dj-database-url
- ✅ `settings_production.py` - Production Django settings
- ✅ `Procfile` - For Heroku compatibility (optional)
