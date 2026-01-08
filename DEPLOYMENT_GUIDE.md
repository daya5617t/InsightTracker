# 🚀 InsightTracker Deployment Guide

## Deployment Options

### Option 1: Deploy to Render (Recommended - Free Tier Available)
### Option 2: Deploy to Railway
### Option 3: Deploy to PythonAnywhere
### Option 4: Deploy to Heroku
### Option 5: Deploy to DigitalOcean/AWS/Azure

---

## 📋 Pre-Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Git repository initialized
- [ ] Environment variables configured
- [ ] Static files collected
- [ ] Database migrations completed
- [ ] Production settings configured

---

## 🎯 Option 1: Render Deployment (Free Tier)

### Step 1: Prepare Project

1. **Update requirements.txt** (already exists)

2. **Create `render.yaml`** (for infrastructure as code)

3. **Create `build.sh`** (build script)

4. **Update settings.py for production**

### Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main
git remote add origin https://github.com/yourusername/insighttracker.git
git push -u origin main
```

### Step 3: Deploy on Render

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: insighttracker
   - **Environment**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn StockPricePrediction.wsgi:application`
   - **Instance Type**: Free

5. Add Environment Variables:
   - `PYTHON_VERSION` = `3.11.0`
   - `SECRET_KEY` = (generate new secret key)
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `your-app.onrender.com`

6. Click "Create Web Service"

**Live URL**: `https://insighttracker.onrender.com`

---

## 🎯 Option 2: Railway Deployment

### Step 1: Install Railway CLI

```bash
npm i -g @railway/cli
```

### Step 2: Login and Deploy

```bash
railway login
railway init
railway up
```

### Step 3: Configure

```bash
railway variables set SECRET_KEY=your-secret-key
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS=*.railway.app
```

**Live URL**: Provided by Railway after deployment

---

## 🎯 Option 3: PythonAnywhere

### Step 1: Create Account
- Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
- Free tier: 1 web app

### Step 2: Upload Project
```bash
# In PythonAnywhere Bash console
git clone https://github.com/yourusername/insighttracker.git
cd insighttracker
mkvirtualenv --python=/usr/bin/python3.10 myenv
pip install -r requirements.txt
```

### Step 3: Configure Web App
1. Go to Web tab → Add a new web app
2. Choose Manual configuration → Python 3.10
3. Set WSGI file path
4. Set static files:
   - URL: `/static/`
   - Directory: `/home/yourusername/insighttracker/static/`

**Live URL**: `http://yourusername.pythonanywhere.com`

---

## 🎯 Option 4: Heroku (Paid - No Free Tier)

### Step 1: Install Heroku CLI
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Login and Create App
```bash
heroku login
heroku create insighttracker
```

### Step 3: Configure and Deploy
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
git push heroku main
heroku run python manage.py migrate
```

**Live URL**: `https://insighttracker.herokuapp.com`

---

## 🎯 Option 5: VPS (DigitalOcean/AWS/Azure)

### Step 1: Create Droplet/Instance
- Ubuntu 22.04 LTS
- 1GB RAM minimum
- SSH access

### Step 2: Server Setup

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install python3.10 python3-pip python3-venv nginx supervisor -y

# Create app user
adduser insighttracker
su - insighttracker

# Clone repository
git clone https://github.com/yourusername/insighttracker.git
cd insighttracker

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Collect static files
python manage.py collectstatic --noinput
python manage.py migrate
```

### Step 3: Configure Gunicorn

Create `/etc/supervisor/conf.d/insighttracker.conf`:
```ini
[program:insighttracker]
directory=/home/insighttracker/insighttracker
command=/home/insighttracker/insighttracker/venv/bin/gunicorn --workers 3 --bind unix:/home/insighttracker/insighttracker.sock StockPricePrediction.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/insighttracker.err.log
stdout_logfile=/var/log/insighttracker.out.log
user=insighttracker
```

### Step 4: Configure Nginx

Create `/etc/nginx/sites-available/insighttracker`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/insighttracker/insighttracker/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/insighttracker/insighttracker.sock;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/insighttracker /etc/nginx/sites-enabled
nginx -t
systemctl restart nginx
supervisorctl reread
supervisorctl update
supervisorctl start insighttracker
```

**Live URL**: `http://your-domain.com`

---

## 🔒 Security Configurations

### 1. Generate New Secret Key

```python
# In Python console
import secrets
print(secrets.token_urlsafe(50))
```

### 2. Environment Variables

Create `.env` file (don't commit to git):
```env
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=sqlite:///db.sqlite3
```

### 3. Update settings.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Security settings
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 📊 Database Options

### SQLite (Development)
- Already configured
- File: `data/database/db.sqlite3`

### PostgreSQL (Production - Recommended)

```bash
pip install psycopg2-binary
```

Update settings.py:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

---

## 📁 Static Files Configuration

### Production Settings

```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# For cloud storage (optional)
# AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
```

Collect static files:
```bash
python manage.py collectstatic --noinput
```

---

## 🔄 CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test
    
    - name: Deploy to Render
      env:
        RENDER_DEPLOY_HOOK: ${{ secrets.RENDER_DEPLOY_HOOK }}
      run: |
        curl $RENDER_DEPLOY_HOOK
```

---

## 🧪 Pre-Deployment Testing

```bash
# Run tests
python manage.py test

# Check for deployment issues
python manage.py check --deploy

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

---

## 📈 Monitoring & Logging

### Option 1: Sentry (Error Tracking)

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

### Option 2: Google Analytics

Add to `base.html`:
```html
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

---

## 🔐 SSL Certificate (HTTPS)

### Let's Encrypt (Free)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

---

## 🚀 Quick Deploy Scripts

I'll create automated deployment scripts in the next step.

---

## 📞 Support & Troubleshooting

### Common Issues

1. **Static files not loading**
   ```bash
   python manage.py collectstatic --clear --noinput
   ```

2. **Database errors**
   ```bash
   python manage.py migrate --run-syncdb
   ```

3. **Permission denied**
   ```bash
   chmod +x build.sh
   ```

### Logs

```bash
# Render: View logs in dashboard
# Railway: railway logs
# PythonAnywhere: Check error log in web tab
# VPS: tail -f /var/log/insighttracker.err.log
```

---

## 📊 Performance Optimization

1. **Enable caching**
   - Redis or Memcached
   
2. **Use CDN**
   - Cloudflare (free)
   - AWS CloudFront

3. **Database optimization**
   - PostgreSQL with connection pooling
   - Database indexes

4. **Compress responses**
   ```python
   MIDDLEWARE = [
       'django.middleware.gzip.GZipMiddleware',
       # ... other middleware
   ]
   ```

---

## ✅ Deployment Checklist

- [ ] Environment variables set
- [ ] Secret key changed
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configured
- [ ] Static files collected
- [ ] Database migrated
- [ ] Superuser created
- [ ] SSL certificate installed
- [ ] Error monitoring setup
- [ ] Backup strategy implemented
- [ ] Domain configured
- [ ] Email service configured (if using alerts)

---

**Choose your deployment method and follow the corresponding section above!**
