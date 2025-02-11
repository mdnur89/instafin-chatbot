from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='base.html'), name='home'),
    path('', include('chatbot.urls')),  # Include chatbot URLs at root level
    path('admin/', admin.site.urls),
    path('chat_platform/', include('chat_platform.urls')),
    path('intelligence/', include('intelligence.urls')),
    path('monitoring/', include('monitoring.urls')),
    path('loans/', include('loan_management.urls')),
    path('communications/', include('communications.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
