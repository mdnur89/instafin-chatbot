from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgeVerificationViewSet, GuardianControlViewSet

router = DefaultRouter()
router.register(r'age-verification', AgeVerificationViewSet, basename='age-verification')
router.register(r'guardian-control', GuardianControlViewSet, basename='guardian-control')

urlpatterns = [
    path('', include(router.urls)),
] 