from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.monitoring_dashboard, name='dashboard'),
    path('analytics/', views.AnalyticsListView.as_view(), name='analytics_list'),
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_log_list'),
    path('metrics/', views.MetricsDashboardView.as_view(), name='metrics_dashboard'),
] 