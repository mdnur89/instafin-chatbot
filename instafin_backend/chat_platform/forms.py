# platforms/forms.py
from django import forms
from .models import ChatPlatform, PlatformCredential, MessageTemplate

class PlatformForm(forms.ModelForm):
    """Form for creating and updating platforms"""
    class Meta:
        model = ChatPlatform
        fields = [
            'name', 'is_active', 'description', 'icon',
            'api_base_url', 'webhook_url', 'api_version',
            'daily_message_quota', 'rate_limit_per_minute'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Add custom validation if needed
        return cleaned_data

class PlatformCredentialForm(forms.ModelForm):
    """Form for managing platform credentials"""
    class Meta:
        model = PlatformCredential
        fields = ['api_key', 'api_secret', 'access_token', 'refresh_token', 'additional_credentials']
        widgets = {
            'api_key': forms.PasswordInput(),
            'api_secret': forms.PasswordInput(),
            'access_token': forms.PasswordInput(),
            'refresh_token': forms.PasswordInput(),
            'additional_credentials': forms.JSONField(),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Add validation for required fields based on platform type
        platform = self.instance.platform
        if platform.name == 'WHATSAPP':
            if not cleaned_data.get('access_token'):
                raise forms.ValidationError("WhatsApp requires an access token")
        return cleaned_data

class MessageTemplateForm(forms.ModelForm):
    """Form for creating and managing message templates"""
    class Meta:
        model = MessageTemplate
        fields = [
            'name', 'template_code', 'content', 'variables',
            'language', 'category', 'is_active'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
            'variables': forms.JSONField(),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_template_code(self):
        template_code = self.cleaned_data.get('template_code')
        # Add validation for template code format
        return template_code