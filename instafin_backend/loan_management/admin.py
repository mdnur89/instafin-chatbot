from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Document, LoanProduct, LoanApplication, LoanDocument,
    RiskAssessment, CommunicationLog, DocumentRequest, AuditLog, DocumentType
)

class UnfoldAdminMixin:
    compressed_fields = []  # Add this to fix the Unfold template error

@admin.register(Document)
class DocumentAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'document_type', 'verification_status', 'uploaded_at', 'is_active')
    list_filter = ('document_type', 'verification_status', 'is_active')
    search_fields = ('user__email', 'document_type')
    readonly_fields = ('uploaded_at', 'verified_at')
    date_hierarchy = 'uploaded_at'

@admin.register(LoanProduct)
class LoanProductAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'min_amount', 'max_amount', 'interest_rate', 'term_months', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

class LoanDocumentInline(admin.TabularInline):
    model = LoanDocument
    extra = 1

@admin.register(LoanApplication)
class LoanApplicationAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'loan_product', 'amount_requested', 'status', 'created_at', 'risk_category')
    list_filter = ('status', 'risk_category')
    search_fields = ('user__email', 'loan_product__name')
    readonly_fields = ('created_at', 'updated_at', 'decision_at')
    inlines = [LoanDocumentInline]
    date_hierarchy = 'created_at'

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('loan_application', 'credit_score', 'risk_category', 'assessment_date', 'manual_override')
    list_filter = ('risk_category', 'manual_override')
    search_fields = ('loan_application__user__email',)
    readonly_fields = ('assessment_date',)

@admin.register(CommunicationLog)
class CommunicationLogAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('loan_application', 'communication_type', 'sent_at', 'sent_by', 'recipient')
    list_filter = ('communication_type',)
    search_fields = ('loan_application__user__email', 'message')
    readonly_fields = ('sent_at',)

@admin.register(DocumentRequest)
class DocumentRequestAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('loan_application', 'document_type', 'status', 'requested_at', 'due_date')
    list_filter = ('document_type', 'status')
    search_fields = ('loan_application__user__email',)
    readonly_fields = ('requested_at',)

@admin.register(AuditLog)
class AuditLogAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'action', 'loan_application', 'document', 'timestamp', 'ip_address')
    list_filter = ('action',)
    search_fields = ('user__email', 'loan_application__user__email')
    readonly_fields = ('timestamp', 'ip_address')

@admin.register(DocumentType)
class DocumentTypeAdmin(UnfoldAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'is_required', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_required',)
