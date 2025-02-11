from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import (
    IntentViewSet,
    ConversationViewSet,
    ConversationTurnViewSet
)
from . import views
from . import consumers

router = DefaultRouter()
router.register(r'intents', IntentViewSet, basename='intent')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'turns', ConversationTurnViewSet, basename='conversation-turn')

app_name = 'chatbot'

urlpatterns = [
    path('api/', include(router.urls)),
    path('chat/', views.ChatWidgetView.as_view(), name='chat_widget'),
    path('chat/message/', views.chat_message, name='chat_message'),
]

# WebSocket URL configuration (add to your routing.py or similar)
websocket_urlpatterns = [
    path('ws/chat/', consumers.ChatbotConsumer.as_asgi()),
] 