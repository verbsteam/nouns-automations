from django.core.management.base import BaseCommand
from django_q.models import Schedule
from django_q.tasks import schedule


class Command(BaseCommand):
    help = 'Schedules a task to continuously check for new Auctions and schedule tasks based on registered webhooks'

    def handle(self, *args, **options):
        schedule(
            func='nouns_triggers.tasks.check_for_new_auction',
            schedule_type=Schedule.MINUTES,
            minutes=5,
            repeats=-1,  # forever
        )

        self.stdout.write(self.style.SUCCESS('Successfully scheduled task'))
