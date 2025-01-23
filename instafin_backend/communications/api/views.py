from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from ..models import AgentAvailability, AgentPerformance, ChatSession, PlatformIntegration
from ..services import AgentManagementService, PlatformIntegrationService
from .serializers import (
    AgentAvailabilitySerializer,
    AgentPerformanceSerializer,
    ChatSessionSerializer,
    PlatformIntegrationSerializer
)

class AgentManagementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing agent availability and performance
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = AgentAvailability.objects.all()
    serializer_class = AgentAvailabilitySerializer

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        agent = self.get_object().agent
        status = request.data.get('status')
        try:
            availability = AgentManagementService.update_agent_status(agent, status)
            return Response(self.get_serializer(availability).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def find_available(self, request):
        skills = request.query_params.getlist('skills', [])
        agent = AgentManagementService.find_available_agent(skills)
        if agent:
            return Response(self.get_serializer(agent).data)
        return Response({'message': 'No available agents'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        agent = self.get_object().agent
        date_str = request.query_params.get('date')
        try:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
            metrics = AgentManagementService.update_performance_metrics(agent, date)
            return Response(AgentPerformanceSerializer(metrics).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PlatformIntegrationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing platform integrations
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = PlatformIntegration.objects.all()
    serializer_class = PlatformIntegrationSerializer

    @action(detail=True, methods=['post'])
    def verify_credentials(self, request, pk=None):
        platform = self.get_object()
        try:
            is_valid = PlatformIntegrationService.verify_credentials(platform)
            return Response({'is_valid': is_valid})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def test_webhook(self, request, pk=None):
        platform = self.get_object()
        try:
            result = PlatformIntegrationService.test_webhook(platform)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 