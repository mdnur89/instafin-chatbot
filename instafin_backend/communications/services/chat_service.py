from django.db import transaction
from ..models import ChatSession, PlatformMessage

class ChatService:
    """Service for managing chat sessions and messages"""

    @staticmethod
    async def get_or_create_session(platform, external_id):
        """Get existing chat session or create new one"""
        try:
            session = await ChatSession.objects.aget(
                platform__platform=platform,
                external_identifier=external_id,
                status='active'
            )
        except ChatSession.DoesNotExist:
            session = await ChatSession.objects.acreate(
                platform=platform,
                external_identifier=external_id,
                status='active'
            )
        return session

    @staticmethod
    async def store_message(session, content, direction='in', metadata=None):
        """Store a new message in the chat session"""
        message = await PlatformMessage.objects.acreate(
            chat_session=session,
            content=content,
            direction=direction,
            metadata=metadata or {}
        )
        return message

    @staticmethod
    async def process_message(session, message_content):
        """Process incoming message and return response"""
        # Store the incoming message
        await ChatService.store_message(session, message_content, 'in')

        # Get chatbot response
        from chatbot.services import ChatbotService
        chatbot = ChatbotService()
        response = await chatbot.process_message(session, message_content)

        # Store the response
        if response:
            await ChatService.store_message(session, response, 'out')

        return response

    @staticmethod
    async def end_session(session):
        """End a chat session"""
        session.status = 'closed'
        session.ended_at = timezone.now()
        await session.asave()
        return session 