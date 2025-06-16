from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.migrations.executor import MigrationExecutor
from django.db import connections
from django.db.utils import OperationalError
from accounts.scheduler import setup_periodic_tasks


class Command(BaseCommand):
    help = "Prepare the application by making migrations, migrating, and collecting static files."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting preparation steps..."))

        # Check if migrations are needed
        self.stdout.write("Checking for pending migrations...")
        if self._has_pending_migrations():
            self.stdout.write(
                "Pending migrations found. Applying migrations..."
            )
            # Make migrations
            self.stdout.write("Making migrations...")
            call_command("makemigrations")

            # Apply migrations
            self.stdout.write("Applying migrations...")
            call_command("migrate")
        else:
            self.stdout.write(
                self.style.SUCCESS("No pending migrations found.")
            )

        # Collect static files
        self.stdout.write("Collecting static files...")
        call_command("collectstatic", "--noinput")

        self.stdout.write("Setting up periodic tasks...")
        setup_periodic_tasks()
        self.stdout.write(
            self.style.SUCCESS("Periodic tasks set successfully.")
        )

        self.stdout.write(
            self.style.SUCCESS(
                "All preparation steps completed successfully."
            )
        )

    def _has_pending_migrations(self):
        """
        Check if there are any pending migrations.
        """
        try:
            connection = connections["default"]
            executor = MigrationExecutor(connection)
            targets = executor.loader.graph.leaf_nodes()
            return executor.migration_plan(targets)
        except OperationalError:
            # If the database is not initialized, assume migrations are needed
            return True
