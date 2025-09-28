from django.contrib import admin
from django.contrib.auth.models import User
from .models import QueueUser, Counter, Employee, UserRequest
from .notifications import notify_all_position_updates

class QueueUserAdmin(admin.ModelAdmin):
    list_display = ('position', 'name', 'token', 'email', 'is_verified', 'otp')
    list_display_links = ('name', 'token')
    search_fields = ('name', 'email', 'token')
    list_filter = ('position', 'is_verified')
    ordering = ('position',)
    readonly_fields = ('token',)
    
    # Custom actions to delete users
    actions = ['delete_selected', 'remove_unverified_selected', 'remove_all_unverified', 'update_queue_positions']
    
    def delete_selected(self, request, queryset):
        """Custom delete action to remove users from queue (mark as served)"""
        count = queryset.count()
        queryset.delete()
        
        # Update positions and send notifications to remaining users
        notify_all_position_updates()
        
        self.message_user(request, f'{count} users have been removed from the queue (marked as served). Position notifications sent to remaining users.')
    delete_selected.short_description = "Remove selected users from queue (mark as served)"
    
    def remove_unverified_selected(self, request, queryset):
        """Delete only the selected users who are not OTP-verified."""
        unverified_qs = queryset.filter(is_verified=False)
        count = unverified_qs.count()
        unverified_qs.delete()
        self.message_user(request, f'{count} unverified user(s) deleted. Verified users were not touched.')
    remove_unverified_selected.short_description = "Delete selected unverified user(s)"

    def remove_all_unverified(self, request, queryset):
        """Delete all unverified users from the system."""
        from .models import QueueUser
        unverified_qs = QueueUser.objects.filter(is_verified=False)
        count = unverified_qs.count()
        unverified_qs.delete()
        self.message_user(request, f'All unverified users deleted ({count}).')
    remove_all_unverified.short_description = "Delete ALL unverified users"
    
    def update_queue_positions(self, request, queryset):
        """Manually update all queue positions and send notifications"""
        notify_all_position_updates()
        self.message_user(request, 'Queue positions updated and notifications sent to users in top 3 positions.')
    update_queue_positions.short_description = "Re-index all queue positions and send notifications"

class CounterAdmin(admin.ModelAdmin):
    list_display = ('number',)
    
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'counter_number', 'is_available')
    list_filter = ('role', 'is_available', 'counter_number')
    search_fields = ('user__username', 'user__email', 'role')
    raw_id_fields = ('user',)

class UserRequestAdmin(admin.ModelAdmin):
    list_display = ('queue_user', 'request_type', 'created_at', 'handled')
    list_filter = ('request_type', 'handled', 'created_at')
    search_fields = ('queue_user__name', 'queue_user__email', 'message')
    actions = ['mark_handled', 'mark_unhandled']

    def mark_handled(self, request, queryset):
        updated = queryset.update(handled=True)
        self.message_user(request, f'Marked {updated} request(s) as handled.')
    mark_handled.short_description = 'Mark selected requests as handled'

    def mark_unhandled(self, request, queryset):
        updated = queryset.update(handled=False)
        self.message_user(request, f'Marked {updated} request(s) as unhandled.')
    mark_unhandled.short_description = 'Mark selected requests as unhandled'

# Customize admin site headers
admin.site.site_header = "Queue Management System Admin"
admin.site.site_title = "QMS Admin"
admin.site.index_title = "Welcome to Queue Management System Administration"

# Register all models
admin.site.register(QueueUser, QueueUserAdmin)
admin.site.register(Counter, CounterAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(UserRequest, UserRequestAdmin)