from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import QueueUser, UserRequest, Employee, QueueConfig
from .notifications import send_welcome_notification, send_call_now_notification
from .email_utils import send_robust_email
from .otp_utils import send_otp_email
import random
import threading
import logging
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db import IntegrityError
from django.db import models
import os

logger = logging.getLogger(__name__)

def reset_all_positions():
    """Reset all user positions to None to ensure clean position assignment"""
    QueueUser.objects.all().update(position=None)

def send_email_in_background(subject, message, recipient_list):
    """Wrapper to send email in a thread and log exceptions."""
    def email_sender():
        try:
            success = send_robust_email(subject, message, recipient_list)
            if not success:
                logger.error(f"Background email sending failed to {recipient_list}. Please check SMTP logs.")
        except Exception as e:
            logger.error(f"Exception in background email thread for {recipient_list}: {e}", exc_info=True)

    email_thread = threading.Thread(target=email_sender)
    email_thread.start()

# -------------------
# Main Pages
# -------------------
def index(request):
    return render(request, 'app1/index.html')


def view_queue(request):
    # Check if user is verified
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please register and verify your email to view the queue.")
        return redirect('register')
    
    try:
        user = QueueUser.objects.get(id=user_id)
        if not user.is_verified:
            messages.error(request, "Please verify your email with OTP to view the queue.")
            return redirect('otp')
    except QueueUser.DoesNotExist:
        messages.error(request, "Invalid session. Please register again.")
        return redirect('register')
    
    # Get all verified queue users ordered by position, but prioritize available users
    queue_users = QueueUser.objects.filter(is_verified=True).order_by('is_available', 'position')
    
    # Get availability status for users ahead in queue
    user_position = user.position if user.position else 0
    users_ahead = QueueUser.objects.filter(
        is_verified=True, 
        position__lt=user_position
    ).order_by('position')
    
    # Calculate statistics
    total_users = queue_users.count()
    current_position = 1 if total_users > 0 else 0
    waiting_count = max(0, total_users - 1)
    
    # Calculate estimated waiting time for each user (15 minutes per person ahead) + global delay
    config = QueueConfig.get()
    global_delay = max(0, int(config.delay_offset_minutes))
    queue_users_with_waiting_time = []
    for user in queue_users:
        # Calculate waiting time: (position - 1) * 15 minutes
        # Position 1 = currently being served (0 wait time)
        # Position 2 = 15 minutes wait, Position 3 = 30 minutes wait, etc.
        # Only add global delay to waiting users (position > 1)
        if user.position == 1:
            estimated_wait_minutes = 0  # Currently serving
        else:
            estimated_wait_minutes = max(0, (user.position - 1) * 15 + global_delay)
        
        # Convert to hours and minutes for better display
        hours = estimated_wait_minutes // 60
        minutes = estimated_wait_minutes % 60
        
        if hours > 0:
            wait_time_display = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        else:
            wait_time_display = f"{minutes}m" if minutes > 0 else "Now serving"
        
        queue_users_with_waiting_time.append({
            'user': user,
            'estimated_wait_minutes': estimated_wait_minutes,
            'wait_time_display': wait_time_display
        })
    
    context = {
        'queue_users': queue_users,
        'queue_users_with_waiting_time': queue_users_with_waiting_time,
        'total_users': total_users,
        'current_position': current_position,
        'waiting_count': waiting_count,
        'users_ahead': users_ahead,
        'current_user': user,
    }
    
    return render(request, 'app1/view_queue.html', context)


def employee(request):
    # Require authentication for employee dashboard
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the current customer (first available verified user in queue)
    current_customer = QueueUser.objects.filter(is_verified=True, is_available=True).order_by('position').first()
    
    # Get all users waiting in the queue (verified users), prioritizing available users
    all_queue_users = QueueUser.objects.filter(is_verified=True).order_by('is_available', 'position')
    
    # Get all unverified users (registered but not verified) - order by ID for consistency
    unverified_users = QueueUser.objects.filter(is_verified=False).order_by('id')

    if request.method == 'POST':
        action = (
            'serve' if 'serve' in request.POST else
            'remove' if 'remove' in request.POST else
            'next' if 'next' in request.POST else
            'add_delay_5' if 'add_delay_5' in request.POST else
            'add_delay_10' if 'add_delay_10' in request.POST else
            'add_delay_15' if 'add_delay_15' in request.POST else
            'reset_delay' if 'reset_delay' in request.POST else
            'notify_next' if 'notify_next' in request.POST else
            None
        )

        if action == 'notify_next' and current_customer:
            # Find the next available user in the queue (position after current)
            next_user = (
                QueueUser.objects
                .filter(is_verified=True, is_available=True, position__gt=current_customer.position)
                .order_by('position')
                .first()
            )
            if next_user:
                def notify_next_sender():
                    try:
                        send_call_now_notification(next_user)
                    except Exception as e:
                        logger.error(f"Exception sending call-now notification to {next_user.email}: {e}", exc_info=True)
                threading.Thread(target=notify_next_sender).start()
                messages.success(request, f"Notification sent to next available user (Token #{next_user.token}).")
            else:
                messages.info(request, "No next available user in the queue to notify.")
            return redirect('employee')

        if action in ('serve', 'remove', 'next') and current_customer:
            # Remove the first customer (served or removed)
            current_customer.delete()

            # Re-number remaining queue positions
            remaining = QueueUser.objects.filter(is_verified=True).order_by('position')
            for idx, user in enumerate(remaining, start=1):
                if user.position != idx:
                    user.position = idx
                    user.save(update_fields=['position'])

            # Notify the new first available user to come for service (if any)
            new_current = QueueUser.objects.filter(is_verified=True, is_available=True).order_by('position').first()
            if new_current:
                def call_now_sender():
                    try:
                        send_call_now_notification(new_current)
                    except Exception as e:
                        logger.error(f"Exception sending call-now notification to {new_current.email}: {e}", exc_info=True)
                threading.Thread(target=call_now_sender).start()

            messages.success(request, 'Moved to next customer.')
            return redirect('employee')

        if action in ('add_delay_5', 'add_delay_10', 'add_delay_15', 'reset_delay'):
            config = QueueConfig.get()
            if action == 'reset_delay':
                config.delay_offset_minutes = 0
                config.save(update_fields=['delay_offset_minutes'])
                messages.success(request, 'Global delay reset to 0 minutes.')
            else:
                inc = 5 if action == 'add_delay_5' else 10 if action == 'add_delay_10' else 15
                config.delay_offset_minutes = max(0, (config.delay_offset_minutes or 0) + inc)
                config.save(update_fields=['delay_offset_minutes'])
                messages.success(request, f'Added {inc} minutes to global waiting time.')
            return redirect('employee')

    context = {
        'name': current_customer.name if current_customer else None,
        'token': current_customer.token if current_customer else None,
        'counter': 1,  # placeholder; wire to Employee model later
        'all_queue_users': all_queue_users,  # All users in queue
        'queue_count': all_queue_users.count(),  # Total count
        'unverified_users': unverified_users,  # Unverified users
        'unverified_count': unverified_users.count(),  # Unverified count
    }

    return render(request, 'app1/employee.html', context)


def login(request):
    """Employee login page. Handles POST authentication and redirects on success."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'app1/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('employee')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'app1/login.html')


def selectCounter(request):
    return render(request, 'app1/selectCounter.html')


def logout(request):
    # Log out authenticated user and clear session
    try:
        auth_logout(request)
    finally:
        request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')


# -------------------
# Registration + OTP
# -------------------
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()

        if not name or not email:
            messages.error(request, "Please fill all the required fields.")
            return redirect('register')

        # Create user without adding to queue yet
        try:
            user = QueueUser.objects.create(
                name=name,
                email=email,
                otp='000000',  # Will be generated when OTP is sent
                position=None  # Don't assign position until verified
            )
        except IntegrityError:
            messages.error(request, "This email is already registered.")
            return redirect('register')

        # Store user_id in session
        request.session['user_id'] = user.id

        # Send OTP email
        def otp_sender():
            try:
                send_otp_email(user)
            except Exception as e:
                logger.error(f"Exception sending OTP email to {user.email}: {e}", exc_info=True)

        otp_thread = threading.Thread(target=otp_sender)
        otp_thread.start()

        messages.success(request, f"Registration initiated! Please check your email for OTP verification. Your token number is #{user.token}")
        return redirect('otp')

    return render(request, 'app1/register.html')


def otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please register first.")
        return redirect('register')
    
    try:
        user = QueueUser.objects.get(id=user_id)
    except QueueUser.DoesNotExist:
        messages.error(request, "Invalid session. Please register again.")
        return redirect('register')
    
    if user.is_verified:
        messages.info(request, "You are already verified!")
        return redirect('success')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'verify':
            entered_otp = request.POST.get('otp', '').strip()
            
            if not entered_otp:
                messages.error(request, "Please enter the OTP.")
                return render(request, 'app1/otp.html', {'user': user})
            
            if user.verify_otp(entered_otp):
                # Assign position in queue after successful verification
                # First, get all verified users (excluding the current user being verified)
                existing_verified_users = QueueUser.objects.filter(is_verified=True).exclude(id=user.id)
                
                if not existing_verified_users.exists():
                    # This is the first verified user, assign position 1
                    user.position = 1
                else:
                    # Get the highest position from existing verified users and add 1
                    last_position = existing_verified_users.aggregate(models.Max('position'))['position__max']
                    user.position = last_position + 1
                
                user.save(update_fields=['position'])
                
                # Send welcome notification
                def notification_sender():
                    try:
                        send_welcome_notification(user)
                    except Exception as e:
                        logger.error(f"Exception in background welcome notification for {user.email}: {e}", exc_info=True)
                
                notification_thread = threading.Thread(target=notification_sender)
                notification_thread.start()
                
                messages.success(request, "OTP verified successfully! You have been added to the queue.")
                return redirect('success')
            else:
                messages.error(request, "Invalid or expired OTP. Please try again.")
        
        elif action == 'resend':
            if user.is_otp_valid():
                messages.info(request, "OTP is still valid. Please check your email or wait before requesting a new one.")
            else:
                def otp_sender():
                    try:
                        send_otp_email(user)
                    except Exception as e:
                        logger.error(f"Exception resending OTP email to {user.email}: {e}", exc_info=True)
                
                otp_thread = threading.Thread(target=otp_sender)
                otp_thread.start()
                
                messages.success(request, "New OTP sent to your email.")
    
    return render(request, 'app1/otp.html', {'user': user})


def success(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please register first.")
        return redirect('register')
    
    try:
        user = QueueUser.objects.get(id=user_id)
        if not user.is_verified:
            messages.error(request, "Please verify your email first.")
            return redirect('otp')
    except QueueUser.DoesNotExist:
        messages.error(request, "Invalid session. Please register again.")
        return redirect('register')
    
    return render(request, 'app1/success.html', {
        'user': user,
        'name': user.name,
        'position': user.position,
        'token': user.token
    })


def reorder_positions():
    """Reorders all verified users to have sequential positions starting from 1"""
    verified_users = QueueUser.objects.filter(is_verified=True).order_by('position')
    for index, user in enumerate(verified_users, 1):
        if user.position != index:
            user.position = index
            user.save(update_fields=['position'])

def toggle_availability(request):
    """Toggle user's availability status."""
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "No active session. Please register/login first.")
        return redirect('register')

    try:
        queue_user = QueueUser.objects.get(id=user_id)
    except QueueUser.DoesNotExist:
        messages.error(request, "Invalid session. Please register again.")
        return redirect('register')

    if not queue_user.is_verified:
        messages.info(request, "Please verify your email first.")
        return redirect('otp')

    # Toggle availability
    queue_user.is_available = not queue_user.is_available
    queue_user.save(update_fields=['is_available'])
    
    status = "available" if queue_user.is_available else "unavailable"
    messages.success(request, f"You are now {status}.")
    return redirect('queue_details')


def cancel_spot(request):
    """Allow the current session user to cancel their spot and leave the queue."""
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "No active session. Please register/login first.")
        return redirect('register')

    try:
        queue_user = QueueUser.objects.get(id=user_id)
    except QueueUser.DoesNotExist:
        messages.error(request, "Invalid session. Please register again.")
        return redirect('register')

    # Only verified users with a position can cancel from queue
    if not queue_user.is_verified or queue_user.position is None:
        messages.info(request, "You are not currently in the queue.")
        return redirect('queue_details')

    # Delete user and reorder the remaining queue
    queue_user.delete()
    remaining = QueueUser.objects.filter(is_verified=True).order_by('position')
    for idx, user in enumerate(remaining, start=1):
        if user.position != idx:
            user.position = idx
            user.save(update_fields=['position'])

    # Clear session user_id since their spot is cancelled
    try:
        del request.session['user_id']
    except KeyError:
        pass

    messages.success(request, "Your spot has been cancelled. Thank you!")
    return redirect('index')

def dashboard(request):
    # Get queue statistics for dashboard (only verified users)
    total_users = QueueUser.objects.filter(is_verified=True).count()
    current_serving = 1 if total_users > 0 else 0
    waiting_count = max(0, total_users - 1)
    
    context = {
        'total_in_queue': total_users,  # Changed from total_users to match template
        'current_serving': current_serving,
        'waiting_count': waiting_count,
        'completed_count': 0,  # Add missing variable
        'cancelled_count': 0,  # Add missing variable
        'recent_entries': [],  # Add missing variable for recent activity table
    }
    
    return render(request, 'app1/dashboard.html', context)

def user_login(request):
    """User login page for existing users to access their queue position."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        name = request.POST.get('name', '').strip()

        if not email or not name:
            messages.error(request, "Email and name are required.")
            return render(request, 'app1/register.html')

        try:
            user = QueueUser.objects.get(email=email, name=name)
            
            # Check if user is verified and in queue
            if user.is_verified and user.position is not None:
                # Store user_id in session
                request.session['user_id'] = user.id
                messages.success(request, f"Welcome back {user.name}! You are in the queue at position {user.position}.")
                return redirect('queue_details')
            else:
                messages.error(request, "You are not currently in the queue. Please register first.")
                return render(request, 'app1/register.html')
                
        except QueueUser.DoesNotExist:
            messages.error(request, "No user found with these credentials. Please check your email and name, or register as a new user.")
            return render(request, 'app1/register.html')

    return render(request, 'app1/register.html')


def submit_request(request):
    """Allow a registered user to submit a textual request to admin."""
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please register first.")
        return redirect('register')

    try:
        queue_user = QueueUser.objects.get(id=user_id)
    except QueueUser.DoesNotExist:
        messages.error(request, "Invalid session. Please register again.")
        return redirect('register')

    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        request_type = request.POST.get('request_type', 'general')
        if not message:
            messages.error(request, "Please enter a message for your request.")
        else:
            user_request = UserRequest.objects.create(
                queue_user=queue_user,
                message=message,
                request_type=request_type
            )
            # Email the admin(s)
            admin_email = os.getenv('ADMIN_EMAIL') or getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
            if admin_email:
                subject = f"User Request: {queue_user.name} ({queue_user.email})"
                body = (
                    f"User: {queue_user.name} (Token #{queue_user.token})\n"
                    f"Email: {queue_user.email}\n"
                    f"Type: {dict(UserRequest.REQUEST_TYPES).get(request_type, request_type)}\n"
                    f"Message:\n{message}\n"
                    f"Request ID: {user_request.id}"
                )
                send_robust_email(subject, body, [admin_email])
            messages.success(request, "Your request has been submitted to the admin.")
            return redirect('queue_details')

    return render(request, 'app1/submit_request.html', {
        'request_types': UserRequest.REQUEST_TYPES,
        'queue_user': queue_user,
    })


def staff_availability(request):
    """Public page showing availability of staff (e.g., doctors, managers)."""
    role = request.GET.get('role', '').strip()
    employees = Employee.objects.all().select_related('user').order_by('user__username')
    if role:
        employees = employees.filter(role__iexact=role)

    roles = (
        Employee.objects
        .values_list('role', flat=True)
        .distinct()
        .order_by('role')
    )

    return render(request, 'app1/staff_availability.html', {
        'employees': employees,
        'roles': roles,
        'active_role': role,
    })