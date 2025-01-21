from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.core.exceptions import PermissionDenied
from .models import (
    Document, LoanProduct, LoanApplication, DocumentRequest,
    RiskAssessment, CommunicationLog, AuditLog
)
from .forms import DocumentUploadForm, LoanApplicationForm, DocumentRequestForm

# Create your views here.

@login_required
def loan_application_create(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='create',
                loan_application=application,
                details={'initial_status': application.status}
            )
            
            messages.success(request, 'Loan application submitted successfully.')
            return redirect('loan_management:application_detail', pk=application.pk)
    else:
        form = LoanApplicationForm()
    
    return render(request, 'loan_management/application_form.html', {'form': form})

@login_required
def loan_application_detail(request, pk):
    application = get_object_or_404(LoanApplication, pk=pk)
    if application.user != request.user and not request.user.is_staff:
        raise PermissionDenied
    
    documents = application.documents.all()
    document_requests = DocumentRequest.objects.filter(loan_application=application)
    risk_assessment = RiskAssessment.objects.filter(loan_application=application).first()
    communications = CommunicationLog.objects.filter(loan_application=application)
    
    context = {
        'application': application,
        'documents': documents,
        'document_requests': document_requests,
        'risk_assessment': risk_assessment,
        'communications': communications,
    }
    return render(request, 'loan_management/application_detail.html', context)

class LoanApplicationListView(ListView):
    model = LoanApplication
    template_name = 'loan_management/application_list.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return LoanApplication.objects.all()
        return LoanApplication.objects.filter(user=self.request.user)

@login_required
def document_upload(request, application_pk):
    application = get_object_or_404(LoanApplication, pk=application_pk)
    if application.user != request.user and not request.user.is_staff:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            
            # Link document to loan application
            application.documents.add(document)
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='create',
                loan_application=application,
                document=document,
                details={'document_type': document.document_type}
            )
            
            messages.success(request, 'Document uploaded successfully.')
            return redirect('loan_management:application_detail', pk=application_pk)
    else:
        form = DocumentUploadForm()
    
    return render(request, 'loan_management/document_upload.html', {'form': form, 'application': application})

@login_required
def document_request_create(request, application_pk):
    if not request.user.is_staff:
        raise PermissionDenied
    
    application = get_object_or_404(LoanApplication, pk=application_pk)
    
    if request.method == 'POST':
        form = DocumentRequestForm(request.POST)
        if form.is_valid():
            document_request = form.save(commit=False)
            document_request.loan_application = application
            document_request.requested_by = request.user
            document_request.save()
            
            # Create communication log
            CommunicationLog.objects.create(
                loan_application=application,
                communication_type='system',
                message=f'Document requested: {document_request.document_type}',
                sent_by=request.user,
                recipient=application.user
            )
            
            messages.success(request, 'Document request created successfully.')
            return redirect('loan_management:application_detail', pk=application_pk)
    else:
        form = DocumentRequestForm()
    
    return render(request, 'loan_management/document_request_form.html', {
        'form': form,
        'application': application
    })
