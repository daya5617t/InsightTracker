"""
Alert Management Views
Add these to the end of views.py
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Watchlist, UserAlertPreferences, PriceAlert
from .alert_service import alert_service
from decimal import Decimal


@login_required
def alert_settings(request):
    """Alert settings and management page"""
    # Get or create user alert preferences
    prefs, created = UserAlertPreferences.objects.get_or_create(user=request.user)
    
    # Handle form submission
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_preferences':
            prefs.email_alerts_enabled = request.POST.get('email_alerts_enabled') == 'on'
            prefs.alert_frequency = request.POST.get('alert_frequency', 'realtime')
            
            # Handle quiet hours
            quiet_start = request.POST.get('quiet_hours_start')
            quiet_end = request.POST.get('quiet_hours_end')
            
            if quiet_start:
                prefs.quiet_hours_start = quiet_start
            if quiet_end:
                prefs.quiet_hours_end = quiet_end
            
            prefs.save()
            messages.success(request, '✓ Alert preferences updated successfully!')
            
        elif action == 'update_watchlist_alert':
            watchlist_id = request.POST.get('watchlist_id')
            watchlist_item = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
            
            watchlist_item.alert_enabled = request.POST.get('alert_enabled') == 'on'
            watchlist_item.alert_on_rise = request.POST.get('alert_on_rise') == 'on'
            watchlist_item.alert_on_fall = request.POST.get('alert_on_fall') == 'on'
            watchlist_item.alert_threshold_percent = Decimal(request.POST.get('alert_threshold_percent', '5.0'))
            watchlist_item.save()
            
            messages.success(request, f'✓ Alert settings updated for {watchlist_item.ticker}!')
        
        return redirect('alert_settings')
    
    # Get user's watchlist with alert info
    watchlist_items = Watchlist.objects.filter(user=request.user).order_by('-created_at')
    
    # Get recent alerts
    recent_alerts = PriceAlert.objects.filter(
        watchlist_item__user=request.user
    ).select_related('watchlist_item').order_by('-sent_at')[:20]
    
    context = {
        'preferences': prefs,
        'watchlist_items': watchlist_items,
        'recent_alerts': recent_alerts,
        'total_alerts': PriceAlert.objects.filter(watchlist_item__user=request.user).count(),
    }
    
    return render(request, 'template/alert_settings.html', context)


@login_required
def toggle_alert(request, watchlist_id):
    """Quick toggle alert for a watchlist item"""
    watchlist_item = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    watchlist_item.alert_enabled = not watchlist_item.alert_enabled
    watchlist_item.save()
    
    status = "enabled" if watchlist_item.alert_enabled else "disabled"
    messages.success(request, f'Alerts {status} for {watchlist_item.ticker}')
    
    return redirect('dashboard')


@login_required
def test_alert(request):
    """Send a test alert email to the user"""
    if request.method == 'POST':
        try:
            # Check if user has any watchlist items
            watchlist_item = Watchlist.objects.filter(user=request.user).first()
            
            if not watchlist_item:
                return JsonResponse({
                    'success': False,
                    'message': 'Please add at least one stock to your watchlist first'
                })
            
            # Send a test alert
            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings
            
            subject = "🎉 Test Alert from InsightTracker"
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 20px auto; padding: 30px; background: #f9fafb; border-radius: 12px; }}
        .header {{ background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%); color: white; padding: 30px; text-align: center; border-radius: 8px; margin-bottom: 20px; }}
        .content {{ background: white; padding: 30px; border-radius: 8px; }}
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">🎉 Test Alert</h1>
            <p style="margin: 10px 0 0 0;">Your email alerts are working perfectly!</p>
        </div>
        <div class="content">
            <p>Hi {request.user.username},</p>
            <p>This is a test email to confirm that your stock price alerts are configured correctly.</p>
            <p><strong>What happens next?</strong></p>
            <ul>
                <li>We'll monitor your watchlist stocks continuously</li>
                <li>You'll receive alerts when prices move beyond your threshold</li>
                <li>Alerts respect your quiet hours settings</li>
            </ul>
            <p>Currently watching: <strong>{Watchlist.objects.filter(user=request.user).count()} stocks</strong></p>
        </div>
        <div class="footer">
            <p>InsightTracker - AI-Powered Stock Analysis</p>
        </div>
    </div>
</body>
</html>
"""
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body="Test alert from InsightTracker",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[request.user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            return JsonResponse({
                'success': True,
                'message': f'Test email sent to {request.user.email}! Check your inbox.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error sending test email: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def bulk_toggle_alerts(request):
    """Enable or disable all alerts at once"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            enable = data.get('enable', True)
            
            # Update all watchlist items for the user
            updated_count = Watchlist.objects.filter(user=request.user).update(
                alert_enabled=enable
            )
            
            action = "enabled" if enable else "disabled"
            return JsonResponse({
                'success': True,
                'message': f'Successfully {action} {updated_count} alerts'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def bulk_adjust_thresholds(request):
    """Adjust all alert thresholds at once"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            adjustment = Decimal(str(data.get('adjustment', 0)))
            adjustment_type = data.get('type', 'increase')
            
            watchlist_items = Watchlist.objects.filter(user=request.user, alert_enabled=True)
            updated_count = 0
            
            for item in watchlist_items:
                if adjustment_type == 'increase':
                    item.alert_threshold_percent += adjustment
                elif adjustment_type == 'decrease':
                    item.alert_threshold_percent = max(Decimal('0.1'), item.alert_threshold_percent - adjustment)
                elif adjustment_type == 'set':
                    item.alert_threshold_percent = adjustment
                
                # Cap at reasonable values
                item.alert_threshold_percent = max(Decimal('0.1'), min(Decimal('100'), item.alert_threshold_percent))
                item.save()
                updated_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully adjusted thresholds for {updated_count} alerts'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def export_alert_history(request):
    """Export alert history as CSV"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="alert_history_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Time', 'Stock', 'Alert Type', 'Price', 'Change %', 'Message'])
    
    # Get all user alerts
    alerts = PriceAlert.objects.filter(
        watchlist_item__user=request.user
    ).select_related('watchlist_item').order_by('-sent_at')[:1000]  # Limit to last 1000
    
    for alert in alerts:
        writer.writerow([
            alert.sent_at.strftime('%Y-%m-%d'),
            alert.sent_at.strftime('%H:%M:%S'),
            alert.watchlist_item.ticker,
            alert.alert_type,
            f'${alert.price_at_alert:.2f}' if alert.price_at_alert else 'N/A',
            f'{alert.percent_change:.2f}%' if alert.percent_change else 'N/A',
            alert.message[:100]  # Truncate long messages
        ])
    
    return response
