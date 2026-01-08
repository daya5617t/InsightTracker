from django.core.management.base import BaseCommand
from ...utils import update_all_data

class Command(BaseCommand):
    help = 'Initialize or update stock and market data'

    def handle(self, *args, **options):
        self.stdout.write('Starting data initialization...')
        update_all_data()
        self.stdout.write(self.style.SUCCESS('Successfully initialized data'))