from django.urls import path
from .views import messenger_webhook

urlpatterns = [
    path('webhook/', messenger_webhook, name='messenger_webhook'),
]