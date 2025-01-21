from django import forms
from .models import Document, LoanApplication, DocumentRequest

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['loan_product', 'amount_requested', 'purpose']
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'amount_requested': forms.NumberInput(attrs={'class': 'form-control'})
        }

    def clean_amount_requested(self):
        amount = self.cleaned_data['amount_requested']
        loan_product = self.cleaned_data.get('loan_product')
        if loan_product:
            if amount < loan_product.min_amount:
                raise forms.ValidationError(f"Amount must be at least {loan_product.min_amount}")
            if amount > loan_product.max_amount:
                raise forms.ValidationError(f"Amount cannot exceed {loan_product.max_amount}")
        return amount

class DocumentRequestForm(forms.ModelForm):
    class Meta:
        model = DocumentRequest
        fields = ['document_type', 'due_date', 'notes']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }