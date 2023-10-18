# payout/management/commands/processpayouts.py
from django.core.management.base import BaseCommand
from payout.tasks import process_payouts

class Command(BaseCommand):
    help = 'Process payouts for eligible transactions'

    def handle(self, *args, **kwargs):
        result = process_payouts.delay()
        self.stdout.write(self.style.SUCCESS(f'Started processing payouts. Task ID: {result.id}'))
