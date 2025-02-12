from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings


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
    email = models.EmailField(null=True, blank=True)
    
    # Identity and verification
    phone_number = models.CharField(
        max_length=20, 
        unique=True, 
        null=True,  # Allow null temporarily for migration
        blank=True
    )
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
    USERNAME_FIELD = 'phone_number'
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
    """Extended user profile with age verification and parental controls"""
    AGE_VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Age Verified'),
        ('minor', 'Verified Minor'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True)
    age_verification_status = models.CharField(max_length=20, choices=AGE_VERIFICATION_STATUS, default='pending')
    guardian_email = models.EmailField(null=True, blank=True)
    guardian_phone = models.CharField(max_length=20, null=True, blank=True)
    guardian_verified = models.BooleanField(default=False)
    restricted_features = models.JSONField(default=list)
    daily_transaction_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    last_guardian_notification = models.DateTimeField(null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['age_verification_status']),
        ]

    def is_minor(self):
        if not self.date_of_birth:
            return False
        today = timezone.now().date()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (
            today.month == self.date_of_birth.month and 
            today.day < self.date_of_birth.day
        ):
            age -= 1
        return age < 18

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

class AgeVerification(models.Model):
    """Handles age verification and parental controls"""
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Age Verified'),
        ('minor', 'Verified Minor'),
        ('rejected', 'Verification Rejected'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='age_verification'
    )
    date_of_birth = models.DateField()
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='pending'
    )
    verification_document = models.ForeignKey(
        'loan_management.Document',
        null=True,
        on_delete=models.SET_NULL,
        related_name='age_verifications'
    )
    verified_at = models.DateTimeField(null=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='verified_age_documents'
    )

    def __str__(self):
        return f"{self.user.email} - {self.verification_status}"

class GuardianControl(models.Model):
    """Manages guardian relationships and controls"""
    minor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='guardian_control'
    )
    guardian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dependents'
    )
    daily_transaction_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True
    )
    restricted_features = models.JSONField(
        default=list,
        help_text="List of restricted features"
    )
    notification_preferences = models.JSONField(
        default=dict,
        help_text="Guardian notification preferences"
    )
    last_notification_sent = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['guardian', 'minor']),
        ]

    def __str__(self):
        return f"Guardian: {self.guardian.email} - Minor: {self.minor.email}"
    