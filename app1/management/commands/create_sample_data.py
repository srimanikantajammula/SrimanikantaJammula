from django.core.management.base import BaseCommand
from app1.models import QueueUser
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Create sample queue data with availability status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sample users to create (default: 10)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Clear existing data
        QueueUser.objects.all().delete()
        self.stdout.write('Cleared existing queue data.')
        
        # Create sample users
        sample_names = [
            'Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson',
            'Emma Brown', 'Frank Miller', 'Grace Lee', 'Henry Taylor',
            'Ivy Chen', 'Jack Anderson', 'Kate Martinez', 'Leo Rodriguez',
            'Maya Patel', 'Noah Kim', 'Olivia White', 'Paul Thompson'
        ]
        
        sample_emails = [
            'alice@example.com', 'bob@example.com', 'carol@example.com', 'david@example.com',
            'emma@example.com', 'frank@example.com', 'grace@example.com', 'henry@example.com',
            'ivy@example.com', 'jack@example.com', 'kate@example.com', 'leo@example.com',
            'maya@example.com', 'noah@example.com', 'olivia@example.com', 'paul@example.com'
        ]
        
        created_users = []
        
        for i in range(min(count, len(sample_names))):
            user = QueueUser.objects.create(
                name=sample_names[i],
                email=sample_emails[i],
                otp='123456',  # Fixed OTP for testing
                is_verified=True,
                position=i + 1,
                is_available=random.choice([True, True, True, False]),  # 75% available
                last_seen=timezone.now()
            )
            created_users.append(user)
            self.stdout.write(f'Created user: {user.name} (Token: {user.token}, Position: {user.position}, Available: {user.is_available})')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(created_users)} sample users with availability status!'
            )
        )
        
        # Show summary
        available_count = QueueUser.objects.filter(is_available=True).count()
        unavailable_count = QueueUser.objects.filter(is_available=False).count()
        
        self.stdout.write(f'Available users: {available_count}')
        self.stdout.write(f'Unavailable users: {unavailable_count}')
