from django.db import models
from django.conf import settings

class Intent(models.Model):
    """Represents different intents that the chatbot can understand"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    training_phrases = models.JSONField(
        help_text="List of example phrases for this intent"
    )
    required_parameters = models.JSONField(
        default=list,
        help_text="Parameters that must be collected for this intent"
    )
    response_templates = models.JSONField(
        help_text="Response templates for different scenarios"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Conversation(models.Model):
    """Tracks conversation state and context"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('waiting_user', 'Waiting for User'),
        ('waiting_agent', 'Waiting for Agent'),
        ('completed', 'Completed'),
    ]

    chat_session = models.ForeignKey('communications.ChatSession', on_delete=models.CASCADE)
    current_intent = models.ForeignKey(Intent, null=True, on_delete=models.SET_NULL)
    context = models.JSONField(
        default=dict,
        help_text="Current conversation context and collected parameters"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    needs_human = models.BooleanField(default=False)
    confidence_score = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.status}"

class ConversationTurn(models.Model):
    """Individual turns in a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user_message = models.TextField()
    bot_response = models.TextField()
    detected_intent = models.ForeignKey(Intent, null=True, on_delete=models.SET_NULL)
    confidence_score = models.FloatField()
    collected_params = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

class EntityType(models.Model):
    """Custom entity types for parameter extraction"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    validation_regex = models.CharField(max_length=255, blank=True)
    examples = models.JSONField(
        help_text="Example values for this entity type"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name