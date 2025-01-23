from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class ChatSession(models.Model):
    CHANNEL_TYPES = [
        ('support', 'Support Chat'),
        ('sales', 'Sales Chat'),
        ('general', 'General Inquiry'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='handled_chats')
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    satisfaction_score = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)

    class Meta:
        ordering = ['timestamp']

class NotificationTemplate(models.Model):
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App Notification'),
        ('push', 'Push Notification'),
    ]

    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Notification(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

class SupportTicket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('technical', 'Technical Issue'),
        ('account', 'Account Related'),
        ('billing', 'Billing Issue'),
        ('loan', 'Loan Related'),
        ('other', 'Other'),
    ]

    ticket_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tickets'
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    satisfaction_score = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Generate ticket number: TKT-YYYYMMDD-XXXX
            last_ticket = SupportTicket.objects.order_by('-id').first()
            if last_ticket:
                last_number = int(last_ticket.ticket_number.split('-')[-1])
                new_number = str(last_number + 1).zfill(4)
            else:
                new_number = '0001'
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            self.ticket_number = f'TKT-{date_str}-{new_number}'
        super().save(*args, **kwargs)

class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='ticket_attachments/', null=True, blank=True)

class CommunicationAuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('status_change', 'Status Changed'),
        ('assignment', 'Assignment Changed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50)  # 'chat', 'notification', 'ticket'
    entity_id = models.IntegerField()
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)

class ChatDocumentSubmission(models.Model):
    """Handles document submissions through chat sessions"""
    VERIFICATION_STATUS = [
        ('pending', 'Pending Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    chat_session = models.ForeignKey('ChatSession', on_delete=models.CASCADE, related_name='document_submissions')
    document_type = models.ForeignKey('loan_management.DocumentType', on_delete=models.PROTECT)
    file = models.FileField(upload_to='chat_documents/%Y/%m/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='chat_verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['verification_status', 'submitted_at']),
        ]

    def __str__(self):
        return f"Document {self.document_type} for {self.chat_session}"

class ChatEscalation(models.Model):
    """Manages chat escalations to live agents"""
    ESCALATION_REASONS = [
        ('complex_query', 'Complex Query'),
        ('user_request', 'User Requested'),
        ('sentiment', 'Negative Sentiment'),
        ('high_value', 'High Value Customer'),
        ('repeated_issue', 'Repeated Issue'),
    ]
    
    PRIORITY_LEVELS = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Urgent'),
    ]

    chat_session = models.ForeignKey('ChatSession', on_delete=models.CASCADE, related_name='escalations')
    reason = models.CharField(max_length=50, choices=ESCALATION_REASONS)
    priority = models.IntegerField(choices=PRIORITY_LEVELS, default=2)
    escalated_at = models.DateTimeField(auto_now_add=True)
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='assigned_escalations'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    auto_escalated = models.BooleanField(default=False)
    sentiment_score = models.FloatField(null=True)
    
    class Meta:
        ordering = ['-priority', '-escalated_at']

class AgentAvailability(models.Model):
    """Tracks agent availability and workload"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('break', 'On Break'),
        ('offline', 'Offline'),
    ]

    agent = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='availability'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    max_concurrent_chats = models.IntegerField(default=3)
    current_chats = models.IntegerField(default=0)
    skills = models.JSONField(
        default=list,
        help_text="List of agent skills (e.g., ['loans', 'technical', 'billing'])"
    )
    last_status_change = models.DateTimeField(auto_now=True)
    auto_assign_enabled = models.BooleanField(default=True)
    working_hours = models.JSONField(
        default=dict,
        help_text="Working hours for each day"
    )

    class Meta:
        verbose_name_plural = "Agent availabilities"
        indexes = [
            models.Index(fields=['status', 'current_chats']),
        ]

    def __str__(self):
        return f"{self.agent.get_full_name()} - {self.status}"

class AgentPerformance(models.Model):
    """Tracks agent performance metrics"""
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='performance_metrics'
    )
    date = models.DateField()
    chats_handled = models.IntegerField(default=0)
    avg_response_time = models.DurationField(null=True)
    avg_resolution_time = models.DurationField(null=True)
    satisfaction_score = models.FloatField(
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    successful_resolutions = models.IntegerField(default=0)
    escalated_chats = models.IntegerField(default=0)

    class Meta:
        unique_together = ['agent', 'date']
        indexes = [
            models.Index(fields=['date', 'agent']),
        ]

    def __str__(self):
        return f"{self.agent.get_full_name()} - {self.date}"

class PlatformIntegration(models.Model):
    """Configuration for different messaging platforms"""
    PLATFORM_TYPES = [
        ('whatsapp', 'WhatsApp'),
        ('messenger', 'Facebook Messenger'),
        ('instagram', 'Instagram'),
        ('web', 'Web Widget')
    ]

    platform = models.CharField(max_length=20, choices=PLATFORM_TYPES)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(
        help_text="Platform-specific configuration (API keys, tokens, etc.)"
    )
    webhook_url = models.URLField(blank=True)
    webhook_secret = models.CharField(max_length=255, blank=True)
    last_health_check = models.DateTimeField(null=True)

class PlatformMessage(models.Model):
    """Messages from external platforms"""
    platform = models.ForeignKey(PlatformIntegration, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=255)
    chat_session = models.ForeignKey('ChatSession', on_delete=models.CASCADE)
    direction = models.CharField(max_length=10, choices=[('in', 'Inbound'), ('out', 'Outbound')])
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
