from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import AgeVerification, GuardianControl
from ..services import AgeVerificationService, GuardianControlService
from .serializers import (
    AgeVerificationSerializer,
    GuardianControlSerializer
)

class AgeVerificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for age verification management
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AgeVerificationSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return AgeVerification.objects.all()
        return AgeVerification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def verify_age(self, request):
        try:
            verification = AgeVerificationService.verify_age(
                user=request.user,
                date_of_birth=request.data.get('date_of_birth'),
                verification_document=request.data.get('document')
            )
            return Response(self.get_serializer(verification).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GuardianControlViewSet(viewsets.ModelViewSet):
    """
    API endpoint for guardian control management
    """
    permission_classes = [IsAuthenticated]
    serializer_class = GuardianControlSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return GuardianControl.objects.all()
        return GuardianControl.objects.filter(
            Q(guardian=user) | Q(minor=user)
        )

    @action(detail=False, methods=['post'])
    def setup_control(self, request):
        try:
            control = GuardianControlService.setup_guardian_control(
                minor_user=request.data.get('minor_user'),
                guardian_user=request.user,
                daily_limit=request.data.get('daily_limit'),
                restricted_features=request.data.get('restricted_features')
            )
            return Response(self.get_serializer(control).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def check_transaction(self, request, pk=None):
        control = self.get_object()
        amount = request.data.get('amount')
        try:
            is_allowed = GuardianControlService.check_transaction_allowed(
                control.minor,
                amount
            )
            return Response({'allowed': is_allowed})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 