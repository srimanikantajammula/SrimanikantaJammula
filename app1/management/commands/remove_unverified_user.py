from django.core.management.base import BaseCommand
from app1.models import QueueUser


class Command(BaseCommand):
    help = (
        'Remove a single unverified (OTP-pending) user by email or ID. '
        'OTP verification process remains unchanged.'
    )

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--email', type=str, help='Email of the unverified user to remove')
        group.add_argument('--id', type=int, help='ID of the unverified user to remove')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without making changes',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        user_id = options.get('id')
        dry_run = options.get('dry_run', False)

        if email:
            queryset = QueueUser.objects.filter(email=email, is_verified=False)
            target_desc = f"email '{email}'"
        else:
            queryset = QueueUser.objects.filter(id=user_id, is_verified=False)
            target_desc = f"ID {user_id}"

        count = queryset.count()
        if count == 0:
            self.stdout.write(self.style.WARNING(
                f'No unverified user found matching {target_desc}. Nothing to do.'
            ))
            return

        user = queryset.first()
        self.stdout.write(
            f"Found unverified user: ID={user.id}, Name='{user.name}', Email='{user.email}', Token=#{user.token}"
        )

        if dry_run:
            self.stdout.write(self.style.NOTICE('Dry-run enabled. No changes made.'))
            return

        deleted_count, _ = queryset.delete()
        if deleted_count:
            self.stdout.write(self.style.SUCCESS(
                f'Successfully removed {deleted_count} unverified user matching {target_desc}.'
            ))
        else:
            self.stdout.write(self.style.WARNING('Unexpectedly deleted 0 users.'))


