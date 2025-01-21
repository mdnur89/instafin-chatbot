from django import forms
from .models import (
    ChatSession, ChatMessage, NotificationTemplate, 
    Notification, SupportTicket, TicketResponse
)

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'chat-message-input'}),
            'attachment': forms.FileInput(attrs={'class': 'file-input'})
        }

class NotificationTemplateForm(forms.ModelForm):
    class Meta:
        model = NotificationTemplate
        fields = ['name', 'subject', 'content', 'channel', 'is_active']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['template', 'title', 'message', 'priority', 'scheduled_for']
        widgets = {
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'message': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'].queryset = NotificationTemplate.objects.filter(is_active=True)

class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['category', 'subject', 'description', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = TicketResponse
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class BulkNotificationForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=NotificationTemplate.objects.filter(is_active=True),
        required=True
    )
    recipients = forms.MultipleChoiceField(
        choices=[],  # Will be populated in __init__
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    scheduled_for = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def __init__(self, *args, **kwargs):
        user_choices = kwargs.pop('user_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['recipients'].choices = user_choices
