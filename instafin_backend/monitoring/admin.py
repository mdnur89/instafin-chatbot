from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import AnalyticsEvent, AuditLog, MetricsSnapshot

@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(ModelAdmin):
    list_display = ('event_type', 'user', 'timestamp', 'platform', 'success', 'duration')
    list_filter = ('event_type', 'platform', 'success', 'timestamp')
    search_fields = ('user__email', 'session_id', 'event_data')
    readonly_fields = ('timestamp',)
    compressed_fields = []

    def has_add_permission(self, request):
        # Analytics events should only be created by the system
        return False

@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ('action', 'user', 'content_type', 'object_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'content_type', 'timestamp')
    search_fields = ('user__email', 'object_id', 'ip_address', 'notes')
    readonly_fields = ('timestamp',)
    compressed_fields = []

    def has_add_permission(self, request):
        # Audit logs should only be created by the system
        return False

@admin.register(MetricsSnapshot)
class MetricsSnapshotAdmin(ModelAdmin):
    list_display = ('date', 'total_users', 'active_users', 'total_chats', 
                   'loan_applications', 'approved_loans', 'rejected_loans')
    list_filter = ('date',)
    readonly_fields = ('date',)
    compressed_fields = []

    fieldsets = (
        ('User Metrics', {
            'fields': ('date', 'total_users', 'active_users')
        }),
        ('Chat Metrics', {
            'fields': ('total_chats', 'completed_chats', 'avg_chat_duration')
        }),
        ('Loan Metrics', {
            'fields': ('loan_applications', 'approved_loans', 'rejected_loans')
        }),
        ('System Metrics', {
            'fields': ('model_accuracy', 'system_errors', 'metrics_data')
        }),
    )
