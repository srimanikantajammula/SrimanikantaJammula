from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app1.models import Employee


class Command(BaseCommand):
    help = 'Create sample staff (doctors, managers) with availability'

    def handle(self, *args, **options):
        staff_definitions = [
            ('doctor_anna', 'Doctor'),
            ('doctor_ben', 'Doctor'),
            ('manager_claire', 'Manager'),
            ('manager_dan', 'Manager'),
        ]

        created = 0
        for idx, (username, role) in enumerate(staff_definitions, start=1):
            user, _ = User.objects.get_or_create(username=username, defaults={
                'email': f'{username}@example.com'
            })
            emp, is_new = Employee.objects.get_or_create(user=user, defaults={
                'counter_number': idx,
                'role': role,
                'is_available': True,
            })
            if is_new:
                created += 1
                self.stdout.write(f'Created {role}: {user.username} (counter {emp.counter_number})')
            else:
                self.stdout.write(f'Exists {role}: {user.username}')

        self.stdout.write(self.style.SUCCESS(f'Staff ready. Newly created: {created}'))

