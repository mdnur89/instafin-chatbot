from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('id_doc', 'Identification Document'),
        ('income_proof', 'Proof of Income'),
        ('bank_statement', 'Bank Statement'),
        ('utility_bill', 'Utility Bill'),
        ('employment_letter', 'Employment Letter'),
        ('other', 'Other'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='loan_documents/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    verification_status = models.CharField(
        max_length=10, 
        choices=VERIFICATION_STATUS,
        default='pending'
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']

class LoanProduct(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()
    required_documents = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LoanApplication(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('pending_documents', 'Pending Documents'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    loan_product = models.ForeignKey(LoanProduct, on_delete=models.PROTECT)
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    documents = models.ManyToManyField(Document, through='LoanDocument')
    credit_score = models.IntegerField(null=True, blank=True)
    risk_category = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    decision_at = models.DateTimeField(null=True, blank=True)
    decision_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='loan_decisions'
    )
    decision_notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

class LoanDocument(models.Model):
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    is_required = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)

class RiskAssessment(models.Model):
    RISK_CATEGORIES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('very_high', 'Very High Risk'),
    ]

    loan_application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE)
    credit_score = models.IntegerField(
        validators=[MinValueValidator(300), MaxValueValidator(850)]
    )
    risk_category = models.CharField(max_length=20, choices=RISK_CATEGORIES)
    assessment_date = models.DateTimeField(auto_now_add=True)
    automated_score = models.IntegerField()
    manual_override = models.BooleanField(default=False)
    override_notes = models.TextField(blank=True)
    assessment_factors = models.JSONField(default=dict)

class CommunicationLog(models.Model):
    COMMUNICATION_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('chatbot', 'Chatbot'),
        ('system', 'System Notification'),
    ]

    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='sent_communications'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_communications'
    )
    metadata = models.JSONField(default=dict, blank=True)

class DocumentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=Document.DOCUMENT_TYPES)
    requested_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

class AuditLog(models.Model):
    ACTION_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed'),
        ('download', 'Downloaded'),
        ('status_change', 'Status Changed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='loan_audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True)
