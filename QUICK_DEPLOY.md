# 🚀 Quick Deploy Guide

## Option 1: Deploy to Render (Recommended - FREE)

### Prerequisites
- GitHub account
- Render account (free signup at render.com)

### Steps

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/insighttracker.git
git push -u origin main
```

2. **Deploy on Render**
   - Go to [render.com](https://render.com) and sign in
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Configure:
     - **Name**: `insighttracker`
     - **Environment**: `Python 3`
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn --chdir StockPricePrediction StockPricePrediction.wsgi:application`
   - Click **"Create Web Service"**

3. **Your app will be live at**: `https://insighttracker.onrender.com`

---

## Option 2: Deploy to Railway (FREE)

### Steps

1. **Install Railway CLI**
```bash
npm i -g @railway/cli
# OR
curl -fsSL https://railway.app/install.sh | sh
```

2. **Deploy**
```bash
railway login
railway init
railway up
```

3. **Set environment variables**
```bash
railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
railway variables set DEBUG=False
```

4. **Your app will be live at**: `https://insighttracker.up.railway.app`

---

## Option 3: Deploy to PythonAnywhere (FREE)

### Steps

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload your project**
   - Go to Files tab
   - Upload zip or use Git

3. **Open Bash console**
```bash
mkvirtualenv --python=/usr/bin/python3.10 myenv
cd insighttracker
pip install -r requirements.txt
```

4. **Configure Web App**
   - Web tab → Add new web app
   - Manual configuration → Python 3.10
   - Set source code: `/home/yourusername/insighttracker/StockPricePrediction`
   - Set WSGI file to point to your project

5. **Your app will be live at**: `http://yourusername.pythonanywhere.com`

---

## 🔧 Environment Variables Needed

For any platform, set these environment variables:

```env
SECRET_KEY=<generate-using-python-secrets>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,*.onrender.com,*.railway.app
```

### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## ✅ Pre-Deployment Checklist

- [ ] Run `python manage.py check --deploy`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Generate new `SECRET_KEY`
- [ ] Run `python manage.py collectstatic`
- [ ] Run `python manage.py migrate`
- [ ] Test locally with `gunicorn`

---

## 🧪 Test Locally Before Deploy

```bash
# Collect static files
cd StockPricePrediction
python manage.py collectstatic --noinput

# Test with gunicorn
gunicorn StockPricePrediction.wsgi:application

# Visit http://localhost:8000
```

---

## 📊 Post-Deployment

1. **Create superuser** (for admin access)
```bash
# On Render/Railway
railway run python StockPricePrediction/manage.py createsuperuser

# On PythonAnywhere (in bash console)
python manage.py createsuperuser
```

2. **Access admin panel**: `https://your-domain.com/admin/`

3. **Monitor logs**
   - Render: Dashboard → Logs
   - Railway: `railway logs`
   - PythonAnywhere: Web tab → Log files

---

## 🔒 Security Reminder

✅ **NEVER commit these to Git:**
- `.env` file
- `db.sqlite3`
- Secret keys
- API keys

✅ **Always:**
- Use environment variables
- Generate new secret key for production
- Set `DEBUG=False`
- Use HTTPS (SSL)

---

## 🆘 Need Help?

Check the full deployment guide: `DEPLOYMENT_GUIDE.md`

**Common Issues:**
- Static files not loading → Run `collectstatic`
- Database errors → Run migrations
- 500 errors → Check logs for details
