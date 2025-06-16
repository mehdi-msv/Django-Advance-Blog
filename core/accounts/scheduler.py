from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


def setup_periodic_tasks():
    """
    Set up periodic tasks with different execution times to avoid overload.
    """

    # Task 1: Reset throttle levels daily at 1:00 AM
    throttle_reset_schedule, _ = CrontabSchedule.objects.get_or_create(
        minute="0",
        hour="1",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )
    PeriodicTask.objects.update_or_create(
        name="Reset Throttle Levels",
        defaults={
            "crontab": throttle_reset_schedule,
            "task": "accounts.tasks.clear_throttle_after_grace",
            "kwargs": json.dumps({}),
        },
    )

    # Task 2: Add monthly score to active users at 1:10 AM
    score_schedule, _ = CrontabSchedule.objects.get_or_create(
        minute="10",
        hour="1",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )
    PeriodicTask.objects.update_or_create(
        name="Monthly Add Score to Active Users",
        defaults={
            "crontab": score_schedule,
            "task": "accounts.tasks.monthly_add_score",
            "kwargs": json.dumps({}),
        },
    )
