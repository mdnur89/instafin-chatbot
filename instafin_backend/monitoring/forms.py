from django import forms
from .models import AnalyticsEvent, AuditLog, MetricsSnapshot

class MetricsSnapshotForm(forms.ModelForm):
    class Meta:
        model = MetricsSnapshot
        fields = '__all__'
        widgets = {
            'metrics_data': forms.Textarea(attrs={'rows': 4, 'class': 'json-editor'}),
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class AnalyticsFilterForm(forms.Form):
    start_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    event_type = forms.ChoiceField(choices=[('', 'All')] + AnalyticsEvent.EVENT_TYPES, required=False)
    platform = forms.CharField(required=False)
    success = forms.BooleanField(required=False)

class AuditLogFilterForm(forms.Form):
    start_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    action = forms.ChoiceField(choices=[('', 'All')] + AuditLog.ACTION_TYPES, required=False)
    user = forms.CharField(required=False)
    content_type = forms.CharField(required=False)