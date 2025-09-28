from django.core.mail import send_mail
from django.conf import settings
import logging
import time
import smtplib
from email.mime.text import MIMEText
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def send_email_via_console(subject, message, recipient_list):
    """
    Console-based email method (bypasses all network issues)
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "="*60)
        print("📧 EMAIL NOTIFICATION (Console Mode)")
        print("="*60)
        print(f"📅 Time: {timestamp}")
        print(f"📤 From: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')}")
        print(f"📥 To: {', '.join(recipient_list)}")
        print(f"📋 Subject: {subject}")
        print("-"*60)
        print("📝 Message:")
        print(message)
        print("="*60)
        print("✅ Email logged to console successfully!")
        print("="*60 + "\n")
        
        # Also log to file for persistence
        log_entry = f"""
[{timestamp}] EMAIL NOTIFICATION
From: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')}
To: {', '.join(recipient_list)}
Subject: {subject}
Message: {message}
{'='*60}
"""
        
        with open('email_log.txt', 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return True
        
    except Exception as e:
        print(f"[CONSOLE] Error logging email: {e}")
        return False

def send_robust_email(subject, message, recipient_list, max_retries=3):
    """
    Send email using Django's SMTP backend with retry logic.
    Returns True if sent successfully, False otherwise.
    """
    logger.info(f"Initiating email send to {recipient_list}")
    
    # Use Django's send_mail with current settings
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting email send (attempt {attempt + 1}/{max_retries})...")
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            
            logger.info(f"Email sent successfully to {recipient_list}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {e}")
            logger.error("Check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env file")
            return False  # Don't retry auth errors
            
        except (smtplib.SMTPConnectError, ConnectionError, OSError) as e:
            logger.error(f"SMTP Connection failed: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                logger.error("All SMTP connection attempts failed")
                return False
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                logger.error("All SMTP attempts failed")
                return False
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    logger.error("Email sending failed after all retry attempts")
    return False

def test_email_connection():
    """
    Test SMTP connection without sending an email.
    Returns True if connection successful, False otherwise.
    """
    try:
        print("[TEST] Testing SMTP connection...")
        host = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        port = int(getattr(settings, 'EMAIL_PORT', 587))
        use_ssl = bool(getattr(settings, 'EMAIL_USE_SSL', False))
        use_tls = bool(getattr(settings, 'EMAIL_USE_TLS', True))

        # Choose correct transport based on settings
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=30)
        else:
            server = smtplib.SMTP(host, port, timeout=30)
            if use_tls:
                server.starttls()

        server.set_debuglevel(0)  # Set to 1 for verbose output
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.quit()

        print("[SUCCESS] SMTP connection test successful!")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERROR] Authentication failed: {e}")
        print("[TIP] Use a Gmail App Password (16 chars), not your regular password")
        return False

    except (smtplib.SMTPConnectError, OSError) as e:
        # OSError covers timeouts like WinError 10060
        print(f"[ERROR] Connection failed: {e}")
        print("[TIP] Check internet/firewall. Open ports 587 (TLS) and/or 465 (SSL).")
        return False

    except Exception as e:
        print(f"[ERROR] Connection test failed: {e}")
        return False
