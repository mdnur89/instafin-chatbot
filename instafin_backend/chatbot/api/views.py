from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Intent, Conversation, ConversationTurn
from ..services import ChatbotService
from .serializers import (
    IntentSerializer,
    ConversationSerializer,
    ConversationTurnSerializer
)
from communications.models import ChatSession
from django.http import HttpResponse
from twilio.request_validator import RequestValidator
from django.conf import settings
from chat_platform.models import PlatformMessage, PlatformHealth

class ChatbotViewSet(viewsets.ViewSet):
    """
    API endpoint for chatbot interactions
    """
    permission_classes = [IsAuthenticated]
    chatbot_service = ChatbotService()

    @action(detail=False, methods=['post'])
    async def send_message(self, request):
        """Send message to chatbot and get response"""
        message_text = request.data.get('message')
        chat_session_id = request.data.get('chat_session_id')
        
        if not message_text or not chat_session_id:
            return Response(
                {'error': 'Message and chat_session_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            chat_session = await ChatSession.objects.aget(id=chat_session_id)
            response = await self.chatbot_service.process_message(
                chat_session,
                message_text
            )
            return Response({'response': response})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def end_conversation(self, request):
        """End current conversation"""
        chat_session_id = request.data.get('chat_session_id')
        try:
            conversation = Conversation.objects.get(
                chat_session_id=chat_session_id,
                status='active'
            )
            conversation.status = 'completed'
            conversation.save()
            return Response({'status': 'conversation ended'})
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'No active conversation found'},
                status=status.HTTP_404_NOT_FOUND
            )

class IntentViewSet(viewsets.ModelViewSet):
    queryset = Intent.objects.all()
    serializer_class = IntentSerializer
    permission_classes = [IsAuthenticated]

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def process_message(self, request, pk=None):
        conversation = self.get_object()
        message = request.data.get('message')
        
        chatbot = ChatbotService()
        response = chatbot.process_message(conversation, message)
        
        return Response({'response': response})

class ConversationTurnViewSet(viewsets.ModelViewSet):
    queryset = ConversationTurn.objects.all()
    serializer_class = ConversationTurnSerializer
    permission_classes = [IsAuthenticated]

@api_view(['POST'])
def twilio_webhook(request):
    """Handle incoming messages and status updates from Twilio"""
    # Validate the request is from Twilio
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    twilio_signature = request.headers.get('X-Twilio-Signature', '')
    
    if not validator.validate(
        request.build_absolute_uri(),
        request.data,
        twilio_signature
    ):
        return HttpResponse(status=403)

    message_status = request.data.get('MessageStatus')
    message_sid = request.data.get('MessageSid')
    
    # Handle message status updates
    if message_status:
        platform_message = PlatformMessage.objects.filter(
            external_id=message_sid
        ).first()
        
        if platform_message:
            platform_message.metadata['delivery_status'] = message_status
            platform_message.save()
            
            # Update health metrics
            PlatformHealth.objects.create(
                platform=platform_message.platform,
                status='UP' if message_status == 'delivered' else 'DEGRADED',
                response_time=0,
                success_rate=100.0 if message_status == 'delivered' else 0.0,
                messages_sent=1,
                messages_failed=0 if message_status == 'delivered' else 1,
                additional_metrics={'twilio_status': message_status}
            )
    
    return HttpResponse(status=200) 