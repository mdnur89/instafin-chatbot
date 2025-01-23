from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    ChatSession, ChatMessage, NotificationTemplate, Notification,
    SupportTicket, TicketResponse, CommunicationAuditLog, ChatDocumentSubmission, ChatEscalation,
    AgentAvailability, AgentPerformance
)

class UnfoldAdminMixin:
    compressed_fields = []  # Required for Unfold theme compatibility

class TicketResponseInline(admin.TabularInline):
    model = TicketResponse
    extra = 0
    readonly_fields = ('created_at',)
    exclude = ('ordering',)
    
    def has_add_permission(self, request, obj=None):
        return True
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_view_permission(self, request, obj=None):
        return True

@admin.register(SupportTicket)
class SupportTicketAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('ticket_number', 'user', 'category', 'subject', 'status', 'priority', 'created_at', 'response_time')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('ticket_number', 'user__email', 'subject', 'description')
    readonly_fields = ('ticket_number', 'created_at', 'updated_at', 'resolved_at')
    inlines = [TicketResponseInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'ticket_number', 'category', 'subject', 'description')
        }),
        ('Status Information', {
            'fields': ('status', 'priority', 'created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return self.readonly_fields + ('user',)
        return self.readonly_fields

    def response_time(self, obj):
        if obj.responses.exists():
            first_response = obj.responses.earliest('created_at')
            duration = first_response.created_at - obj.created_at
            hours = duration.total_seconds() / 3600
            return f"{hours:.1f} hours"
        return "-"
    response_time.short_description = "First Response Time"

    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new ticket
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, TicketResponse):
                instance.responder = request.user
                if instance.ticket.status == 'pending':
                    instance.ticket.status = 'in_progress'
                    instance.ticket.save()
            instance.save()
        formset.save_m2m()

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'channel', 'subject', 'is_active', 'created_at')
    list_filter = ('channel', 'is_active', 'created_at')
    search_fields = ('name', 'subject', 'content')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Notification)
class NotificationAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('recipient', 'title', 'status', 'priority', 'scheduled_for', 'sent_at')
    list_filter = ('status', 'priority', 'template__channel', 'sent_at')
    search_fields = ('recipient__email', 'title', 'message')
    readonly_fields = ('sent_at', 'read_at')
    date_hierarchy = 'scheduled_for'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'template')

@admin.register(ChatSession)
class ChatSessionAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'agent', 'channel_type', 'status', 'started_at', 'duration')
    list_filter = ('channel_type', 'status', 'started_at')
    search_fields = ('user__email', 'agent__email')
    readonly_fields = ('started_at',)
    
    def duration(self, obj):
        if obj.ended_at:
            duration = obj.ended_at - obj.started_at
            return f"{duration.seconds // 60} minutes"
        return "Ongoing"

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('timestamp',)

@admin.register(CommunicationAuditLog)
class CommunicationAuditLogAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'entity_type', 'entity_id')
    list_filter = ('action', 'entity_type', 'timestamp')
    search_fields = ('user__email', 'description')
    readonly_fields = ('timestamp', 'ip_address')

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(ChatDocumentSubmission)
class ChatDocumentSubmissionAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('chat_session', 'document_type', 'verification_status', 'submitted_at', 'verified_by')
    list_filter = ('verification_status', 'document_type', 'submitted_at')
    search_fields = ('chat_session__user__email', 'notes')
    readonly_fields = ('submitted_at', 'verified_at')

@admin.register(ChatEscalation)
class ChatEscalationAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('chat_session', 'reason', 'priority', 'escalated_at', 'assigned_agent', 'resolved_at')
    list_filter = ('reason', 'priority', 'auto_escalated')
    search_fields = ('chat_session__user__email', 'resolution_notes')
    readonly_fields = ('escalated_at', 'sentiment_score')

@admin.register(AgentAvailability)
class AgentAvailabilityAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('agent', 'status', 'current_chats', 'max_concurrent_chats', 'auto_assign_enabled')
    list_filter = ('status', 'auto_assign_enabled')
    search_fields = ('agent__email', 'agent__first_name', 'agent__last_name')
    readonly_fields = ('last_status_change',)

@admin.register(AgentPerformance)
class AgentPerformanceAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('agent', 'date', 'chats_handled', 'avg_response_time', 'satisfaction_score')
    list_filter = ('date',)
    search_fields = ('agent__email',)
    date_hierarchy = 'date'
