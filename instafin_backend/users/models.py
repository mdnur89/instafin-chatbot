from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


# At the top of your models.py, add:
from .managers import CustomUserManager

class User(AbstractUser):
    """Extended user model with additional fields for user management."""
    
    class ContactPreference(models.TextChoices):
        SMS = 'SMS', _('SMS')
        EMAIL = 'EMAIL', _('Email')
        WHATSAPP = 'WHATSAPP', _('WhatsApp')
        IN_APP = 'IN_APP', _('In-App')
    
    class Language(models.TextChoices):
        ENGLISH = 'EN', _('English')
        SPANISH = 'ES', _('Spanish')
        FRENCH = 'FR', _('French')
    
    # Remove username field and make email required
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Identity and verification
    phone_number = models.CharField(max_length=15, unique=True, null=True)
    date_of_birth = models.DateField(null=True)
    national_id = models.CharField(max_length=20, unique=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Financial indicators
    credit_score = models.IntegerField(null=True, blank=True)
    risk_level = models.CharField(max_length=20, blank=True)
    current_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Specify email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    # Add the custom manager
    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['national_id']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class UserProfile(models.Model):
    """Detailed user profile information."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    employment_status = models.CharField(max_length=50, null=True)
    income_range = models.CharField(max_length=50, null=True)
    address = models.JSONField(null=True)
    employment_details = models.JSONField(null=True)
    metadata = models.JSONField(default=dict)

class UserPreferences(models.Model):
    """User communication and system preferences."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_language = models.CharField(
        max_length=2,
        choices=User.Language.choices,
        default=User.Language.ENGLISH
    )
    preferred_contact = models.CharField(
        max_length=10,
        choices=User.ContactPreference.choices,
        default=User.ContactPreference.EMAIL
    )
    marketing_opt_in = models.BooleanField(default=False)
    notification_preferences = models.JSONField(default=dict)
    communication_channels = models.JSONField(default=dict)
    active_channels = models.JSONField(default=dict)
    custom_preferences = models.JSONField(default=dict)

class PreferenceHistory(models.Model):
    """Track changes in user preferences."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preference_history')
    changed_field = models.CharField(max_length=50)
    old_value = models.JSONField()
    new_value = models.JSONField()
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='preference_changes')
    change_reason = models.CharField(max_length=200, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'changed_field', 'timestamp']),
        ]

class UserCommunication(models.Model):
    """Track all communications with the user."""
    
    class Status(models.TextChoices):
        SENT = 'SENT', _('Sent')
        DELIVERED = 'DELIVERED', _('Delivered')
        READ = 'READ', _('Read')
        FAILED = 'FAILED', _('Failed')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communications')
    channel = models.CharField(max_length=10, choices=User.ContactPreference.choices)
    message_type = models.CharField(max_length=50)
    content = models.JSONField()
    status = models.CharField(max_length=20, choices=Status.choices)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True)
    read_at = models.DateTimeField(null=True)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'channel', 'sent_at']),
            models.Index(fields=['status', 'sent_at']),
        ]

class UserFeedback(models.Model):
    """Model to store user feedback and ratings."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    category = models.CharField(max_length=50)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    feedback_text = models.TextField()
    interaction_id = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'category', 'created_at']),
        ]

class UserEngagementMetrics(models.Model):
    """Model to track user engagement metrics."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='engagement_metrics')
    engagement_score = models.FloatField(default=0.0)
    last_login_date = models.DateTimeField(null=True)
    total_interactions = models.PositiveIntegerField(default=0)
    interaction_frequency = models.JSONField(default=dict)
    channel_engagement = models.JSONField(default=dict)
    response_rates = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'User engagement metrics'
    