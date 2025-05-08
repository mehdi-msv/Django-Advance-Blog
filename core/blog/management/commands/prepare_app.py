from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Prepare the application by making migrations, migrating, and collecting static files.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting preparation steps...'))

        # Make migrations
        self.stdout.write('Making migrations...')
        call_command('makemigrations')

        # Apply migrations
        self.stdout.write('Applying migrations...')
        call_command('migrate')

        # Collect static files
        self.stdout.write('Collecting static files...')
        call_command('collectstatic', '--noinput')

        self.stdout.write(self.style.SUCCESS('All preparation steps completed successfully.'))