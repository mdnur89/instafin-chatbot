from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import (
    IntentViewSet,
    ConversationViewSet,
    ConversationTurnViewSet
)

router = DefaultRouter()
router.register(r'intents', IntentViewSet, basename='intent')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'turns', ConversationTurnViewSet, basename='conversation-turn')

app_name = 'chatbot'

urlpatterns = [
    path('api/', include(router.urls)),
] 