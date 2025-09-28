from django.core.mail import send_mail
from django.conf import settings
from .email_utils import send_robust_email
import logging

logger = logging.getLogger(__name__)

def send_otp_email(user):
    """Send OTP verification email to user"""
    try:
        otp = user.generate_otp()
        
        subject = "Queue Management System - OTP Verification"
        message = f"""
Dear {user.name},

Your OTP for joining the queue is: {otp}

This OTP is valid for 10 minutes only. Please enter this code to complete your registration.

Token Number: #{user.token}

Best regards,
Queue Management System
        """
        
        success = send_robust_email(subject, message, [user.email])
        
        if success:
            logger.info(f"OTP email sent successfully to {user.email}")
            return True
        else:
            logger.error(f"Failed to send OTP email to {user.email}")
            return False
            
    except Exception as e:
        logger.error(f"Exception sending OTP email to {user.email}: {e}", exc_info=True)
        return False
