from rest_framework import serializers
from ..models import (
    AgentAvailability,
    AgentPerformance,
    ChatSession,
    PlatformIntegration,
    PlatformMessage
)

class AgentAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentAvailability
        fields = [
            'id', 'agent', 'status', 'last_status_change',
            'current_chats', 'max_concurrent_chats',
            'auto_assign_enabled', 'skills'
        ]

class AgentPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentPerformance
        fields = [
            'id', 'agent', 'date', 'chats_handled',
            'successful_resolutions', 'escalated_chats',
            'avg_satisfaction'
        ]

class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = [
            'id', 'platform', 'external_identifier',
            'agent', 'status', 'started_at', 'ended_at',
            'satisfaction_score'
        ]

class PlatformIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformIntegration
        fields = [
            'id', 'platform', 'is_active', 'config',
            'webhook_url', 'webhook_secret', 'last_health_check'
        ]
        extra_kwargs = {
            'webhook_secret': {'write_only': True},
            'config': {'write_only': True}
        }

class PlatformMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformMessage
        fields = [
            'id', 'platform', 'external_id', 'chat_session',
            'direction', 'content', 'metadata', 'timestamp'
        ] 