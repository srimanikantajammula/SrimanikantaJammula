from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
from datetime import datetime, timedelta

class Counter(models.Model):
    number = models.IntegerField(unique=True)
    
    def __str__(self):
        return f"Counter {self.number}"

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    counter_number = models.IntegerField(default=0)
    role = models.CharField(max_length=50, default='Staff')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} (Counter: {self.counter_number})"

class QueueUser(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    token = models.IntegerField(default=0)
    position = models.IntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    def generate_otp(self):
        """Generate a 6-digit OTP and set creation time"""
        self.otp = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save(update_fields=['otp', 'otp_created_at'])
        return self.otp
    
    def is_otp_valid(self):
        """Check if OTP is still valid (within 10 minutes)"""
        if not self.otp_created_at:
            return False
        expiry_time = self.otp_created_at + timedelta(minutes=10)
        return timezone.now() <= expiry_time
    
    def verify_otp(self, entered_otp):
        """Verify the entered OTP"""
        if self.otp == entered_otp and self.is_otp_valid():
            self.is_verified = True
            self.save(update_fields=['is_verified'])
            return True
        return False
    
    def save(self, *args, **kwargs):
        if self.pk is None:  # Only on creation
            # Assign a random token
            self.token = random.randint(1000, 9999)
            
            # Determine the next position safely
            last_position = QueueUser.objects.aggregate(models.Max('position'))['position__max']
            if last_position is None:
                self.position = 1
            else:
                self.position = last_position + 1
                
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} (Token: {self.token})"


class QueueConfig(models.Model):
    """Global queue configuration (singleton-like)."""
    delay_offset_minutes = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"QueueConfig(delay_offset_minutes={self.delay_offset_minutes})"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class UserRequest(models.Model):
    REQUEST_TYPES = (
        ('general', 'General'),
        ('late', 'Running Late'),
        ('forward', 'Request Forward in Queue'),
        ('help', 'Need Assistance'),
    )

    queue_user = models.ForeignKey(QueueUser, on_delete=models.CASCADE, related_name='requests')
    message = models.TextField(max_length=1000)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    handled = models.BooleanField(default=False)
    handled_note = models.TextField(blank=True)

    def __str__(self):
        return f"Request by {self.queue_user.name} [{self.get_request_type_display()}]"