from django.db import transaction
from .models import QueueUser
from .email_utils import send_robust_email
import logging

logger = logging.getLogger(__name__)

def send_position_notification(user, new_position):
    """Send email notification when user's position changes"""
    
    if new_position <= 3:  # Notify when user is in top 3 positions
        subject = f"Your Queue Position Update - Token #{user.token}"
        
        if new_position == 1:
            message = f"""
Hello {user.name},

GREAT NEWS! You are now NEXT in line!

Your Details:
- Token Number: #{user.token}
- Current Position: {new_position}
- Status: You're next to be served!

Please be ready and stay near the service area.
Queue Management System Team
            """
        elif new_position == 2:
            message = f"""
Hello {user.name},

You're almost there! Only 1 person ahead of you.

Your Details:
- Token Number: #{user.token}
- Current Position: {new_position}
- Status: Please get ready, you'll be called soon!

Queue Management System Team
            """
        elif new_position == 3:
            message = f"""
Hello {user.name},

Your turn is approaching! Only 2 people ahead of you.

Your Details:
- Token Number: #{user.token}
- Current Position: {new_position}
- Status: Please prepare to be served soon

Queue Management System Team
            """
        
        return send_robust_email(subject, message.strip(), [user.email])
    
    return False


@transaction.atomic
def notify_all_position_updates():
    """Re-index all users in the queue and send notifications if their position changes."""
    # Lock the table to prevent race conditions
    users = list(QueueUser.objects.select_for_update().order_by('position'))
    
    for index, user in enumerate(users, 1):
        if user.position != index:
            old_position = user.position
            user.position = index
            # Use update_fields to avoid triggering the save() method's side effects again
            user.save(update_fields=['position'])
            # Notify user about their new position
            send_position_notification(user, index)
            logger.info(f"Updated {user.name}: Position {old_position} -> {index}")


def send_welcome_notification(user):
    """Send welcome notification when user first joins the queue (optional)"""
    subject = f"Welcome to Queue - Token #{user.token}"
    
    message = f"""
Hello {user.name},

Welcome to our Queue Management System! You have successfully joined the queue.

Your Queue Details:
- Token Number: #{user.token}
- Current Position: {user.position}

What happens next?
- You'll receive email updates as your position changes
- When you're in the top 3, we'll send priority notifications

Queue Management System Team
    """
    # Use the robust email function which handles failures gracefully
    return send_robust_email(subject, message.strip(), [user.email])


def send_call_now_notification(user):
    """Notify the user that it is their turn now (position 1)."""
    subject = f"It's Your Turn - Token #{user.token}"
    message = f"""
Hello {user.name},

It's your turn now. Please come to the service counter.

Your Details:
- Token Number: #{user.token}
- Current Position: {user.position}

Thank you,
Queue Management System Team
    """
    return send_robust_email(subject, message.strip(), [user.email])
