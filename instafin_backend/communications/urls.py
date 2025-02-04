from django.urls import path, include
from . import views
from .webhooks.twilio import twilio_webhook
from .api.urls import router as api_router

app_name = 'communications'

urlpatterns = [
    # Chat URLs
    path('chat-sessions/', views.ChatSessionListView.as_view(), name='chat_session_list'),
    path('chat-sessions/<int:session_id>/', views.chat_session_detail, name='chat_session_detail'),
    path('chat-sessions/new/', views.start_new_chat, name='start_new_chat'),
    
    # Notification URLs
    path('notifications/templates/', views.notification_template_list, name='notification_template_list'),
    path('notifications/templates/create/', views.notification_template_create, name='notification_template_create'),
    path('notifications/bulk-send/', views.send_bulk_notification, name='send_bulk_notification'),
    
    # Support Ticket URLs
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/<str:ticket_number>/', views.ticket_detail, name='ticket_detail'),

    path('api/', include(api_router.urls)),
    path('webhooks/twilio/', twilio_webhook, name='twilio-webhook'),
] 