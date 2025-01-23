from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgentManagementViewSet

router = DefaultRouter()
router.register(r'agents', AgentManagementViewSet, basename='agent')

urlpatterns = [
    path('', include(router.urls)),
] 