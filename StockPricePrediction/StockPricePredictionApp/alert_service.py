"""
Stock Price Alert Service
Monitors watchlist stocks and sends email alerts when prices move significantly
"""

import yfinance as yf
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Watchlist, PriceAlert, UserAlertPreferences
import logging

logger = logging.getLogger(__name__)


class StockAlertService:
    """Service to monitor stocks and send price alerts"""
    
    def __init__(self):
        self.checked_count = 0
        self.alerts_sent = 0
        
    def check_all_watchlists(self):
        """Check all active watchlist items for price changes"""
        logger.info("Starting watchlist price check...")
        
        # Get all watchlist items with alerts enabled
        watchlist_items = Watchlist.objects.filter(
            alert_enabled=True,
            user__alert_preferences__email_alerts_enabled=True
        ).select_related('user', 'user__alert_preferences')
        
        logger.info(f"Found {watchlist_items.count()} watchlist items to check")
        
        for item in watchlist_items:
            try:
                self.check_stock(item)
                self.checked_count += 1
            except Exception as e:
                logger.error(f"Error checking {item.ticker} for {item.user.username}: {e}")
                
        logger.info(f"Completed check: {self.checked_count} stocks checked, {self.alerts_sent} alerts sent")
        return {
            'checked': self.checked_count,
            'alerts_sent': self.alerts_sent
        }
    
    def check_stock(self, watchlist_item):
        """Check a single stock for price changes"""
        ticker_symbol = watchlist_item.ticker
        
        try:
            # Fetch current price
            ticker = yf.Ticker(ticker_symbol)
            current_price = self.get_current_price(ticker)
            
            if current_price is None:
                logger.warning(f"Could not fetch price for {ticker_symbol}")
                return
            
            # If no last_price, this is first check - just store the price
            if watchlist_item.last_price is None:
                watchlist_item.last_price = Decimal(str(current_price))
                watchlist_item.last_checked = timezone.now()
                watchlist_item.save()
                logger.info(f"Initial price set for {ticker_symbol}: ${current_price}")
                return
            
            # Calculate price change
            old_price = float(watchlist_item.last_price)
            change_percent = ((current_price - old_price) / old_price) * 100
            
            # Check if alert should be triggered
            threshold = float(watchlist_item.alert_threshold_percent)
            
            should_alert = False
            alert_type = None
            
            if change_percent >= threshold and watchlist_item.alert_on_rise:
                should_alert = True
                alert_type = 'rise'
            elif change_percent <= -threshold and watchlist_item.alert_on_fall:
                should_alert = True
                alert_type = 'fall'
            
            if should_alert:
                # Check quiet hours
                if self.is_quiet_hours(watchlist_item.user):
                    logger.info(f"Skipping alert for {ticker_symbol} - quiet hours")
                    return
                
                # Send alert
                self.send_price_alert(
                    watchlist_item=watchlist_item,
                    alert_type=alert_type,
                    old_price=old_price,
                    new_price=current_price,
                    change_percent=change_percent
                )
                
                # Update last price after alert
                watchlist_item.last_price = Decimal(str(current_price))
                watchlist_item.last_checked = timezone.now()
                watchlist_item.save()
                
                self.alerts_sent += 1
            else:
                # Update last checked time even if no alert
                watchlist_item.last_checked = timezone.now()
                watchlist_item.save()
                
        except Exception as e:
            logger.error(f"Error checking stock {ticker_symbol}: {e}")
            raise
    
    def get_current_price(self, ticker):
        """Get current stock price"""
        try:
            # Try fast_info first
            info = ticker.fast_info
            price = info.get('lastPrice') or info.get('regularMarketPrice')
            if price:
                return float(price)
        except:
            pass
        
        try:
            # Fallback to history
            hist = ticker.history(period='1d', interval='1m')
            if not hist.empty and 'Close' in hist.columns:
                return float(hist['Close'].iloc[-1])
        except:
            pass
        
        return None
    
    def is_quiet_hours(self, user):
        """Check if current time is within user's quiet hours"""
        try:
            prefs = user.alert_preferences
            if not prefs.quiet_hours_start or not prefs.quiet_hours_end:
                return False
            
            now = timezone.now().time()
            start = prefs.quiet_hours_start
            end = prefs.quiet_hours_end
            
            if start < end:
                # Normal case: 10 PM to 8 AM
                return start <= now <= end
            else:
                # Crosses midnight: 8 AM to 10 PM
                return now >= start or now <= end
        except:
            return False
    
    def send_price_alert(self, watchlist_item, alert_type, old_price, new_price, change_percent):
        """Send email alert for price change"""
        user = watchlist_item.user
        ticker = watchlist_item.ticker
        
        # Create alert record
        alert = PriceAlert.objects.create(
            watchlist_item=watchlist_item,
            alert_type=alert_type,
            old_price=Decimal(str(old_price)),
            new_price=Decimal(str(new_price)),
            change_percent=Decimal(str(round(change_percent, 2)))
        )
        
        # Prepare email
        direction = "UP" if alert_type == 'rise' else "DOWN"
        emoji = "🚀" if alert_type == 'rise' else "📉"
        color = "#22c55e" if alert_type == 'rise' else "#ef4444"
        
        subject = f"{emoji} {ticker} Alert: Price {direction} {abs(change_percent):.2f}%"
        
        # Email context
        context = {
            'user': user,
            'ticker': ticker,
            'alert_type': alert_type,
            'direction': direction,
            'emoji': emoji,
            'color': color,
            'old_price': f"${old_price:.2f}",
            'new_price': f"${new_price:.2f}",
            'change_percent': f"{change_percent:+.2f}",
            'abs_change_percent': f"{abs(change_percent):.2f}",
            'timestamp': timezone.now().strftime('%B %d, %Y at %I:%M %p'),
        }
        
        # Create HTML email
        html_content = self.create_html_email(context)
        text_content = strip_tags(html_content)
        
        try:
            # Send email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            # Mark as sent
            alert.email_sent = True
            alert.save()
            
            logger.info(f"Alert sent to {user.email} for {ticker}: {direction} {change_percent:.2f}%")
            
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {e}")
            raise
    
    def create_html_email(self, context):
        """Create beautiful HTML email"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            margin: 0;
            padding: 0;
            background-color: #f3f4f6;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: #ffffff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, {context['color']} 0%, {context['color']}dd 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            font-weight: 800;
        }}
        .header .emoji {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .alert-box {{
            background: #f9fafb;
            border-left: 4px solid {context['color']};
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .price-info {{
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
            padding: 20px;
            background: #f9fafb;
            border-radius: 12px;
        }}
        .price-box {{
            text-align: center;
        }}
        .price-label {{
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}
        .price-value {{
            font-size: 24px;
            font-weight: 700;
            color: #1f2937;
        }}
        .change-badge {{
            display: inline-block;
            background: {context['color']};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 18px;
        }}
        .cta-button {{
            display: inline-block;
            background: {context['color']};
            color: white;
            padding: 14px 32px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 20px;
        }}
        .footer {{
            background: #f9fafb;
            padding: 30px;
            text-align: center;
            font-size: 13px;
            color: #6b7280;
        }}
        .footer a {{
            color: {context['color']};
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="emoji">{context['emoji']}</div>
            <h1>{context['ticker']} Price Alert</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Price movement detected on your watchlist</p>
        </div>
        
        <div class="content">
            <div class="alert-box">
                <h2 style="margin-top: 0; color: {context['color']};">Price {context['direction']} Alert</h2>
                <p>Hi {context['user'].username},</p>
                <p><strong>{context['ticker']}</strong> has moved <span class="change-badge">{context['change_percent']}%</span> and triggered your watchlist alert.</p>
            </div>
            
            <div class="price-info">
                <div class="price-box">
                    <div class="price-label">Previous Price</div>
                    <div class="price-value">{context['old_price']}</div>
                </div>
                <div class="price-box">
                    <div class="price-label">Current Price</div>
                    <div class="price-value" style="color: {context['color']};">{context['new_price']}</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="http://127.0.0.1:8000/details/{context['ticker']}" class="cta-button">
                    View {context['ticker']} Details →
                </a>
            </div>
            
            <div style="margin-top: 30px; padding-top: 30px; border-top: 1px solid #e5e7eb;">
                <p style="font-size: 13px; color: #6b7280;">
                    <strong>Alert triggered:</strong> {context['timestamp']}<br>
                    <strong>Threshold:</strong> Your alert is set for {context['abs_change_percent']}% movements
                </p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>InsightTracker</strong> - AI-Powered Stock Analysis</p>
            <p>
                <a href="http://127.0.0.1:8000/dashboard/">Dashboard</a> • 
                <a href="http://127.0.0.1:8000/dashboard/">Manage Alerts</a> • 
                <a href="http://127.0.0.1:8000/dashboard/">Watchlist</a>
            </p>
            <p style="margin-top: 20px; font-size: 11px;">
                You're receiving this because you enabled price alerts for {context['ticker']}.<br>
                To stop receiving alerts for this stock, remove it from your watchlist.
            </p>
        </div>
    </div>
</body>
</html>
"""
        return html


# Singleton instance
alert_service = StockAlertService()
