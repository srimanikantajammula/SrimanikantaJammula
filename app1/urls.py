from django.urls import path
from . import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', views.index, name='index'),  # Root of app1
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('user-login/', views.user_login, name='user_login'),
    path('queue-details/', views.view_queue, name='queue_details'),
    path('otp/', views.otp, name='otp'),  # Email OTP page
    path('login/', views.login, name='login'),
    # Backward-compatible redirect for /employee/login -> /login
    path('employee/login/', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('employee/', views.employee, name='employee'),
    path('logout/', views.logout, name='logout'),
    path('success/', views.success, name='success'),
    path('request/', views.submit_request, name='submit_request'),
    path('cancel-spot/', views.cancel_spot, name='cancel_spot'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('staff-availability/', views.staff_availability, name='staff_availability'),

    path('selectCounter/', views.selectCounter, name='selectCounter'),
]
