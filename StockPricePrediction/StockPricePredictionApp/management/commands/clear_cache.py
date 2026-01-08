from django.core.management.base import BaseCommand
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Clear all cache data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing cache...')
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS('Successfully cleared cache'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error clearing cache: {str(e)}'))