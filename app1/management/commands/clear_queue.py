from django.core.management.base import BaseCommand
from app1.models import QueueUser

class Command(BaseCommand):
    help = 'Clear all users from the queue'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmed',
            action='store_true',
            help='Confirm that you want to clear all users from the queue',
        )

    def handle(self, *args, **options):
        if not options['confirmed']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL users from the queue. Use --confirmed to proceed.'
                )
            )
            return

        # Count users before deletion
        total_users = QueueUser.objects.count()
        verified_users = QueueUser.objects.filter(is_verified=True).count()
        unverified_users = QueueUser.objects.filter(is_verified=False).count()

        self.stdout.write(f'Found {total_users} total users:')
        self.stdout.write(f'  - {verified_users} verified users in queue')
        self.stdout.write(f'  - {unverified_users} unverified users')

        if total_users == 0:
            self.stdout.write(self.style.SUCCESS('No users to delete.'))
            return

        # First reset all positions to None for clean assignment
        QueueUser.objects.all().update(position=None)
        self.stdout.write('Reset all user positions to None.')

        # Delete all users
        QueueUser.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {total_users} users from the queue and reset positions.'
            )
        )
