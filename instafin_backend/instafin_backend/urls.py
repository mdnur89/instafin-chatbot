from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("chat_platform/", include("chat_platform.urls")),
    path("intelligence/", include("intelligence.urls")),
    path("monitoring/", include("monitoring.urls")),
    path("loans/", include("loan_management.urls")),
    path("communications/", include("communications.urls")),
    path("chatbot/", include("chatbot.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
