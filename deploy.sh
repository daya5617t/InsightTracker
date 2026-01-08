#!/bin/bash

echo "🚀 InsightTracker Deployment Script"
echo "====================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git branch -M main
    print_success "Git initialized"
else
    print_success "Git already initialized"
fi

# Generate secret key
echo ""
echo "Generating Django secret key..."
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
print_success "Secret key generated: ${SECRET_KEY:0:20}..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cat > .env << EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
    print_success ".env file created"
else
    print_warning ".env file already exists"
fi

# Make build.sh executable
chmod +x build.sh
print_success "build.sh made executable"

# Install dependencies
echo ""
echo "Installing production dependencies..."
pip install gunicorn whitenoise python-dotenv
print_success "Production dependencies installed"

# Collect static files
echo ""
echo "Collecting static files..."
cd StockPricePrediction
python manage.py collectstatic --noinput
cd ..
print_success "Static files collected"

# Run migrations
echo ""
echo "Running database migrations..."
cd StockPricePrediction
python manage.py migrate
cd ..
print_success "Migrations completed"

# Git setup
echo ""
echo "Setting up Git..."
git add .
git commit -m "Prepare for deployment" || print_warning "No changes to commit"
print_success "Git commit completed"

echo ""
echo "====================================="
echo "✅ Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Push to GitHub:"
echo "   git remote add origin https://github.com/yourusername/insighttracker.git"
echo "   git push -u origin main"
echo ""
echo "2. Deploy to platform of choice:"
echo "   - Render: Connect GitHub repo at render.com"
echo "   - Railway: Run 'railway init && railway up'"
echo "   - Heroku: Run 'heroku create && git push heroku main'"
echo ""
echo "Your secret key: $SECRET_KEY"
echo "Store this securely!"
