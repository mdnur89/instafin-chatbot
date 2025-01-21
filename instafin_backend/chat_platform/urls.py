from django.urls import path
from . import views

app_name = 'chat_platform'

urlpatterns = [
    # Platform views
    path('', views.PlatformListView.as_view(), name='platform_list'),
    path('create/', views.PlatformCreateView.as_view(), name='platform_create'),
    path('<int:pk>/', views.PlatformDetailView.as_view(), name='platform_detail'),
    path('<int:pk>/update/', views.PlatformUpdateView.as_view(), name='platform_update'),
    path('health/', views.PlatformHealthView.as_view(), name='platform_health'),
    
    # Template views
    path('templates/', views.MessageTemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.MessageTemplateCreateView.as_view(), name='template_create'),
    
    # API endpoints
    path('webhook/<str:platform>/', views.PlatformWebhookView.as_view(), name='platform_webhook'),
    path('api/templates/<str:platform>/', views.TemplateAPIView.as_view(), name='template_api'),
]