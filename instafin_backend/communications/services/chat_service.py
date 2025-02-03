from django.db import transaction
from ..models import ChatSession, PlatformMessage, PlatformIntegration
from django.utils import timezone
from django.contrib.auth import get_user_model
from chatbot.models import Conversation
import logging
from intelligence.services import FAQMatchingService

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatService:
    """Service for managing chat sessions and messages"""

    @staticmethod
    async def get_or_create_session(platform, external_id):
        """Get existing chat session or create new one"""
        try:
            # Clean up the phone number
            phone_number = external_id.replace('whatsapp:', '')
            
            # Get or create user - using afilter().afirst() for async
            user = await User.objects.filter(phone_number=phone_number).afirst()
            if not user:
                user = await User.objects.acreate(
                    phone_number=phone_number,
                    is_active=True,
                    is_verified=False,
                )

            # Get or create chat session
            session = await ChatSession.objects.filter(
                channel_type=platform,
                user=user,
                status='active'
            ).afirst()

            if not session:
                session = await ChatSession.objects.acreate(
                    channel_type=platform,
                    user=user,
                    status='active'
                )

            # Get or create conversation for the chatbot
            conversation = await Conversation.objects.filter(
                chat_session=session
            ).afirst()

            if not conversation:
                conversation = await Conversation.objects.acreate(
                    chat_session=session,
                    status='active',
                    context={}
                )

        except Exception as e:
            print(f"Error in get_or_create_session: {str(e)}")
            raise

        return session

    @staticmethod
    async def store_message(session, content, direction='in', metadata=None):
        """Store a new message in the chat session"""
        # Get the platform from the session's channel_type
        platform_integration = await PlatformIntegration.objects.filter(
            platform=session.channel_type
        ).afirst()
        
        if not platform_integration:
            raise ValueError(f"No platform integration found for {session.channel_type}")
        
        message = await PlatformMessage.objects.acreate(
            chat_session=session,
            platform=platform_integration,
            content=content,
            direction=direction,
            metadata=metadata or {}
        )
        return message

    @staticmethod
    async def process_message(session, message_content):
        """Process incoming message and return response"""
        try:
            # Use proper async query
            conversation = await Conversation.objects.filter(
                chat_session=session,
                status='active'
            ).afirst()

            if not conversation:
                conversation = await Conversation.objects.acreate(
                    chat_session=session,
                    status='active',
                    context={}
                )

            # Process message and get response
            response = await ChatService._get_chatbot_response(conversation, message_content)
            
            # Store the response
            await ChatService.store_message(
                session=session,
                content=response,
                direction='out'
            )

            return response
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")
            return "I'm having trouble processing your message. Please try again."

    @staticmethod
    async def end_session(session):
        """End a chat session"""
        session.status = 'closed'
        session.ended_at = timezone.now()
        await session.asave()
        return session

    @staticmethod
    async def _get_chatbot_response(conversation, message):
        """Get response from chatbot"""
        try:
            # First check if there's a matching FAQ
            faq_match = await FAQMatchingService.find_matching_faq(message)
            
            if faq_match and faq_match['confidence'] > 0.7:
                return faq_match['answer']
            
            # If no FAQ match, fall back to default response
            # TODO: Implement actual chatbot logic here
            return "Thank you for your message. How can I help you today?"
        except Exception as e:
            logger.error(f"Chatbot error: {str(e)}")
            return "I'm having trouble processing your message. Please try again." 