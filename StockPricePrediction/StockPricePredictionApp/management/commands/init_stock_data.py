from django.core.management.base import BaseCommand
from ...init_data import initialize_stock_data

class Command(BaseCommand):
    help = 'Initialize stock data for the application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data initialization...')
        try:
            success = initialize_stock_data()
            if success:
                self.stdout.write(self.style.SUCCESS('Successfully initialized stock data'))
            else:
                self.stdout.write(self.style.ERROR('Failed to initialize stock data'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error initializing data: {str(e)}'))