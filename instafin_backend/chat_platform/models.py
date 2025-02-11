# platforms/models.py
from django.db import models
from django.core.validators import URLValidator
from django.utils import timezone

class ChatPlatform(models.Model):
    """Main platform model for different messaging services"""
    PLATFORM_CHOICES = [
        ('WHATSAPP', 'WhatsApp'),
        ('FACEBOOK', 'Facebook Messenger'),
        ('INSTAGRAM', 'Instagram'),
        ('TWITTER', 'Twitter'),
        ('WEB', 'Web Widget'),
        ('MOBILE_SDK', 'Mobile SDK'),
    ]

    name = models.CharField(max_length=50, choices=PLATFORM_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    icon = models.ImageField(upload_to='platform_icons/', null=True, blank=True)
    
    # Platform configuration
    api_base_url = models.CharField(max_length=255, validators=[URLValidator()], null=True)
    webhook_url = models.CharField(max_length=255, validators=[URLValidator()], null=True)
    api_version = models.CharField(max_length=20, null=True)
    
    # Rate limiting and quotas
    daily_message_quota = models.IntegerField(default=1000)
    rate_limit_per_minute = models.IntegerField(default=60)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_health_check = models.DateTimeField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['name', 'is_active']),
        ]

    def __str__(self):
        return f"{self.get_name_display()} ({self.api_version})"

class PlatformCredential(models.Model):
    """Store encrypted credentials for each platform"""
    platform = models.OneToOneField(ChatPlatform, on_delete=models.CASCADE, related_name='credentials')
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True)
    additional_credentials = models.JSONField(default=dict)  # For platform-specific credentials
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MessageTemplate(models.Model):
    """Templates for different types of messages on each platform"""
    platform = models.ForeignKey(ChatPlatform, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=100)
    template_code = models.CharField(max_length=100, unique=True)
    content = models.TextField()
    variables = models.JSONField()  # List of variables in the template
    language = models.CharField(max_length=10, default='en')
    
    # Template metadata
    category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    approval_status = models.CharField(max_length=20, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['platform', 'template_code', 'language']

class PlatformHealth(models.Model):
    """Track platform health and performance metrics"""
    platform = models.ForeignKey(ChatPlatform, on_delete=models.CASCADE, related_name='health_logs')
    status = models.CharField(max_length=20)  # UP, DOWN, DEGRADED
    response_time = models.FloatField()  # in milliseconds
    error_count = models.IntegerField(default=0)
    success_rate = models.FloatField()  # percentage
    messages_sent = models.IntegerField(default=0)
    messages_failed = models.IntegerField(default=0)
    
    check_timestamp = models.DateTimeField(default=timezone.now)
    additional_metrics = models.JSONField(default=dict)

    class Meta:
        indexes = [
            models.Index(fields=['platform', 'check_timestamp']),
        ]

class PlatformMessage(models.Model):
    """Model for storing platform message details"""
    platform = models.ForeignKey(ChatPlatform, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=255)  # Message ID from platform
    chat_session = models.ForeignKey(
        'communications.ChatSession',
        on_delete=models.CASCADE,
        related_name='platform_messages'
    )
    direction = models.CharField(max_length=10, choices=[('in', 'Incoming'), ('out', 'Outgoing')])
    content = models.JSONField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['external_id']),
            models.Index(fields=['chat_session', 'created_at']),
        ]