from rest_framework import serializers
from ..models import Intent, Conversation, ConversationTurn

class IntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intent
        fields = [
            'id', 'name', 'description', 'training_phrases',
            'required_parameters', 'response_templates'
        ]

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            'id', 'chat_session', 'status', 'context',
            'started_at', 'ended_at'
        ]

class ConversationTurnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationTurn
        fields = [
            'id', 'conversation', 'user_message',
            'bot_response', 'intent', 'confidence_score',
            'parameters', 'timestamp'
        ]