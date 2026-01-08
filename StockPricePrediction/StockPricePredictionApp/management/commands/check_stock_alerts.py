"""
Django management command to check watchlist stocks and send alerts
Run this with: python manage.py check_stock_alerts
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from StockPricePredictionApp.alert_service import alert_service


class Command(BaseCommand):
    help = 'Check all watchlist stocks for price changes and send email alerts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ticker',
            type=str,
            help='Check specific ticker only',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\nStock Alert Check Started\n{timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n{"="*60}\n'
        ))

        try:
            if options['ticker']:
                # Check specific ticker
                from StockPricePredictionApp.models import Watchlist
                items = Watchlist.objects.filter(ticker=options['ticker'], alert_enabled=True)
                
                if not items.exists():
                    self.stdout.write(self.style.WARNING(
                        f'No watchlist items found for ticker: {options["ticker"]}'
                    ))
                    return
                
                self.stdout.write(f'Checking {items.count()} watchlist items for {options["ticker"]}...\n')
                
                for item in items:
                    try:
                        alert_service.check_stock(item)
                        self.stdout.write(self.style.SUCCESS(f'✓ Checked {item.ticker} for {item.user.username}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'✗ Error checking {item.ticker}: {e}'))
            else:
                # Check all watchlists
                results = alert_service.check_all_watchlists()
                
                self.stdout.write(self.style.SUCCESS(
                    f'\n{"="*60}\n'
                    f'✓ Check Complete!\n'
                    f'  Stocks Checked: {results["checked"]}\n'
                    f'  Alerts Sent: {results["alerts_sent"]}\n'
                    f'{"="*60}\n'
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error: {str(e)}\n'))
            raise

        self.stdout.write(self.style.SUCCESS(f'Finished at {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n'))
