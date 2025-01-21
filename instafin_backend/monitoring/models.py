from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class AnalyticsEvent(models.Model):
    """Track various analytics events across the system"""
    EVENT_TYPES = [
        ('chat_started', 'Chat Started'),
        ('chat_completed', 'Chat Completed'),
        ('loan_applied', 'Loan Applied'),
        ('loan_approved', 'Loan Approved'),
        ('loan_rejected', 'Loan Rejected'),
        ('model_trained', 'Model Trained'),
        ('user_registered', 'User Registered'),
    ]

    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    session_id = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    platform = models.CharField(max_length=50, blank=True)
    success = models.BooleanField(default=True)
    duration = models.IntegerField(null=True, blank=True, help_text="Duration in seconds")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"

class AuditLog(models.Model):
    """Track all system changes and important events"""
    ACTION_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('login', 'Logged In'),
        ('logout', 'Logged Out'),
        ('view', 'Viewed'),
        ('export', 'Exported'),
        ('status_change', 'Status Changed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='monitoring_audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')
    changes = models.JSONField(default=dict, help_text="Record of changes made")
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"

class MetricsSnapshot(models.Model):
    """Daily snapshot of key system metrics"""
    date = models.DateField(unique=True)
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    total_chats = models.IntegerField(default=0)
    completed_chats = models.IntegerField(default=0)
    avg_chat_duration = models.FloatField(null=True, blank=True)
    loan_applications = models.IntegerField(default=0)
    approved_loans = models.IntegerField(default=0)
    rejected_loans = models.IntegerField(default=0)
    model_accuracy = models.FloatField(null=True, blank=True)
    system_errors = models.IntegerField(default=0)
    metrics_data = models.JSONField(default=dict, help_text="Additional metrics")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Metrics for {self.date}"