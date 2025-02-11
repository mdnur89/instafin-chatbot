from django.urls import path
from .views import twilio_webhook

urlpatterns = [
    # ... existing urls ...
    path('webhook/twilio/', twilio_webhook, name='twilio_webhook'),
] 