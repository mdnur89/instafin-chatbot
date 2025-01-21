from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    # Chat URLs
    path('chats/', views.chat_session_list, name='chat_session_list'),
    path('chats/<int:session_id>/', views.chat_session_detail, name='chat_session_detail'),
    
    # Notification URLs
    path('notifications/templates/', views.notification_template_list, name='notification_template_list'),
    path('notifications/templates/create/', views.notification_template_create, name='notification_template_create'),
    path('notifications/bulk-send/', views.send_bulk_notification, name='send_bulk_notification'),
    
    # Support Ticket URLs
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/<str:ticket_number>/', views.ticket_detail, name='ticket_detail'),
] 