from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

def setup_periodic_tasks():
    """
    creates or gets a crontab schedule to run every day at 1:00 AM,
    and then creates or updates a periodic task that calls the
    'monthly_add_score' task for verified users.
    """
    # Create or get a crontab schedule for running every day at 1:00 AM
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='1',
        day_of_week='*',
        day_of_month='*',
        month_of_year='*',
    )

    # Create or update a periodic task for adding score to active users monthly
    PeriodicTask.objects.update_or_create(
        name="Monthly Add Score to Active Users",
        defaults={
            "crontab": schedule,
            "task": "accounts.tasks.monthly_add_score",
            "kwargs": json.dumps({}),
        },
    )
