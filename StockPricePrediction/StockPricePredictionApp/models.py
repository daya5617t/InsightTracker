from django.db import models
from django.contrib.auth.models import User

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist', db_index=True)
    ticker = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Alert settings
    alert_enabled = models.BooleanField(default=True, db_index=True)
    alert_on_rise = models.BooleanField(default=True)
    alert_on_fall = models.BooleanField(default=True)
    alert_threshold_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)  # Alert if price moves 5%
    
    # Price tracking
    last_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    last_checked = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'ticker')  # Prevent duplicate entries for same user/ticker
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ticker', 'alert_enabled']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.ticker}"


class UserAlertPreferences(models.Model):
    """Global alert preferences for each user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alert_preferences')
    email_alerts_enabled = models.BooleanField(default=True)
    alert_frequency = models.CharField(
        max_length=20,
        choices=[
            ('realtime', 'Real-time (Immediate)'),
            ('hourly', 'Hourly Digest'),
            ('daily', 'Daily Digest'),
        ],
        default='realtime'
    )
    quiet_hours_start = models.TimeField(null=True, blank=True)  # e.g., 10:00 PM
    quiet_hours_end = models.TimeField(null=True, blank=True)    # e.g., 8:00 AM
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Alert Preferences - {self.user.username}"


class PriceAlert(models.Model):
    """Log of all price alerts sent"""
    watchlist_item = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(
        max_length=10,
        choices=[
            ('rise', 'Price Rise'),
            ('fall', 'Price Fall'),
        ]
    )
    old_price = models.DecimalField(max_digits=15, decimal_places=2)
    new_price = models.DecimalField(max_digits=15, decimal_places=2)
    change_percent = models.DecimalField(max_digits=5, decimal_places=2)
    email_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.watchlist_item.ticker} - {self.alert_type} - {self.change_percent}%"


# ============================================================================
# PORTFOLIO TRACKER MODELS
# ============================================================================

class Portfolio(models.Model):
    """User's investment portfolio"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios', db_index=True)
    name = models.CharField(max_length=100, default="My Portfolio")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def total_value(self):
        """Calculate current portfolio value"""
        import yfinance as yf
        total = 0
        for holding in self.holdings.all():
            try:
                stock = yf.Ticker(holding.ticker)
                current_price = stock.info.get('currentPrice', 0)
                total += current_price * holding.shares
            except:
                total += holding.purchase_price * holding.shares
        return round(total, 2)
    
    def total_invested(self):
        """Calculate total amount invested"""
        return sum(h.purchase_price * h.shares for h in self.holdings.all())
    
    def total_gain_loss(self):
        """Calculate total profit/loss"""
        return self.total_value() - self.total_invested()
    
    def total_gain_loss_percent(self):
        """Calculate percentage gain/loss"""
        invested = self.total_invested()
        if invested == 0:
            return 0
        return round((self.total_gain_loss() / invested) * 100, 2)


class PortfolioHolding(models.Model):
    """Individual stock holdings in a portfolio"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='holdings', db_index=True)
    ticker = models.CharField(max_length=20, db_index=True)
    shares = models.DecimalField(max_digits=15, decimal_places=4)
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2)
    purchase_date = models.DateField(db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['portfolio', 'ticker']),
            models.Index(fields=['ticker', '-purchase_date']),
        ]
    
    def __str__(self):
        return f"{self.ticker} - {self.shares} shares"
    
    def current_price(self):
        """Get current stock price"""
        import yfinance as yf
        try:
            stock = yf.Ticker(self.ticker)
            return stock.info.get('currentPrice', self.purchase_price)
        except:
            return self.purchase_price
    
    def current_value(self):
        """Calculate current value of holding"""
        return round(float(self.current_price()) * float(self.shares), 2)
    
    def cost_basis(self):
        """Calculate original investment"""
        return round(float(self.purchase_price) * float(self.shares), 2)
    
    def gain_loss(self):
        """Calculate profit/loss"""
        return self.current_value() - self.cost_basis()
    
    def gain_loss_percent(self):
        """Calculate percentage gain/loss"""
        cost = self.cost_basis()
        if cost == 0:
            return 0
        return round((self.gain_loss() / cost) * 100, 2)


class Transaction(models.Model):
    """Track all buy/sell transactions"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='transactions', db_index=True)
    ticker = models.CharField(max_length=20, db_index=True)
    transaction_type = models.CharField(
        max_length=4,
        choices=[
            ('BUY', 'Buy'),
            ('SELL', 'Sell'),
        ],
        db_index=True
    )
    shares = models.DecimalField(max_digits=15, decimal_places=4)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateField(db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['portfolio', '-transaction_date']),
            models.Index(fields=['ticker', '-transaction_date']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} {self.shares} {self.ticker} @ ${self.price}"


# ============================================================================
# NEWS & SENTIMENT MODELS
# ============================================================================

class NewsArticle(models.Model):
    """Cache news articles with sentiment analysis"""
    ticker = models.CharField(max_length=20, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=1000)
    source = models.CharField(max_length=100, db_index=True)
    published_at = models.DateTimeField(db_index=True)
    image_url = models.URLField(max_length=1000, blank=True)
    
    # Sentiment analysis
    sentiment_score = models.FloatField(default=0)  # -1 to 1
    sentiment_label = models.CharField(
        max_length=10,
        choices=[
            ('positive', 'Positive'),
            ('neutral', 'Neutral'),
            ('negative', 'Negative'),
        ],
        default='neutral',
        db_index=True
    )
    
    fetched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-published_at']
        unique_together = ('ticker', 'url')
        indexes = [
            models.Index(fields=['ticker', '-published_at']),
            models.Index(fields=['sentiment_label', '-published_at']),
        ]
    
    def __str__(self):
        return f"{self.ticker} - {self.title[:50]}"


class StockScreenerTemplate(models.Model):
    """Save custom screener configurations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='screener_templates')
    name = models.CharField(max_length=100)
    filters = models.JSONField()  # Store filter criteria as JSON
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
