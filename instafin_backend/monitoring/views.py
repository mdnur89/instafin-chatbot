from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import AnalyticsEvent, AuditLog, MetricsSnapshot
from .forms import AnalyticsFilterForm, AuditLogFilterForm
from django.shortcuts import render
import json
from django.contrib.auth.decorators import login_required

class AnalyticsListView(LoginRequiredMixin, ListView):
    model = AnalyticsEvent
    template_name = 'monitoring/analytics_list.html'
    context_object_name = 'events'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        form = AnalyticsFilterForm(self.request.GET)
        
        if form.is_valid():
            if form.cleaned_data['start_date']:
                queryset = queryset.filter(timestamp__gte=form.cleaned_data['start_date'])
            if form.cleaned_data['end_date']:
                queryset = queryset.filter(timestamp__lte=form.cleaned_data['end_date'])
            if form.cleaned_data['event_type']:
                queryset = queryset.filter(event_type=form.cleaned_data['event_type'])
            if form.cleaned_data['platform']:
                queryset = queryset.filter(platform=form.cleaned_data['platform'])
            if form.cleaned_data['success'] is not None:
                queryset = queryset.filter(success=form.cleaned_data['success'])
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = AnalyticsFilterForm(self.request.GET)
        
        # Add summary statistics
        queryset = self.get_queryset()
        context['stats'] = {
            'total_events': queryset.count(),
            'success_rate': queryset.filter(success=True).count() * 100 / max(queryset.count(), 1),
            'event_breakdown': queryset.values('event_type').annotate(count=Count('id')),
            'avg_duration': queryset.filter(duration__isnull=False).aggregate(Avg('duration'))['duration__avg']
        }
        return context

class AuditLogListView(LoginRequiredMixin, ListView):
    model = AuditLog
    template_name = 'monitoring/audit_log_list.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        form = AuditLogFilterForm(self.request.GET)
        
        if form.is_valid():
            if form.cleaned_data['start_date']:
                queryset = queryset.filter(timestamp__gte=form.cleaned_data['start_date'])
            if form.cleaned_data['end_date']:
                queryset = queryset.filter(timestamp__lte=form.cleaned_data['end_date'])
            if form.cleaned_data['action']:
                queryset = queryset.filter(action=form.cleaned_data['action'])
            if form.cleaned_data['user']:
                queryset = queryset.filter(user__email__icontains=form.cleaned_data['user'])
            if form.cleaned_data['content_type']:
                queryset = queryset.filter(content_type__model__icontains=form.cleaned_data['content_type'])
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = AuditLogFilterForm(self.request.GET)
        return context

class MetricsDashboardView(LoginRequiredMixin, DetailView):
    model = MetricsSnapshot
    template_name = 'monitoring/metrics_dashboard.html'
    context_object_name = 'metrics'

    def get_object(self):
        # Get the latest metrics snapshot
        return MetricsSnapshot.objects.first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add historical data for charts
        last_30_days = timezone.now().date() - timedelta(days=30)
        context['historical_data'] = MetricsSnapshot.objects.filter(
            date__gte=last_30_days
        ).order_by('date')
        
        return context

@login_required
def monitoring_dashboard(request):
    context = {
        'metrics': get_metrics(),
        'historical_data_json': json.dumps(get_historical_data())
    }
    return render(request, 'monitoring/metrics_dashboard.html', context)

def get_metrics():
    # Get latest metrics snapshot
    latest_metrics = MetricsSnapshot.objects.first()
    return latest_metrics or {}

def get_historical_data():
    # Get last 30 days of metrics
    historical_data = MetricsSnapshot.objects.all()[:30]
    return [
        {
            'date': metric.date.strftime('%Y-%m-%d'),
            'active_users': metric.active_users,
            'loan_applications': metric.loan_applications
        }
        for metric in historical_data
    ]