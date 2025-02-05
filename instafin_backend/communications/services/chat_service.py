from django.db import transaction
from ..models import ChatSession, PlatformMessage, PlatformIntegration
from django.utils import timezone
from django.contrib.auth import get_user_model
from chatbot.models import Conversation
import logging
from intelligence.services import FAQMatchingService
from .auth_service import ChatAuthenticationService
from .menu_service import ChatMenuService
# from .dummy_data import DummyDataStore
from .api_service import InstafinAPIService
from django.db.models import Q, F
from intelligence.models import FAQ
from typing import Optional
from django.db import models

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatService:
    """Service for managing chat sessions and messages"""

    GREETING_MESSAGES = [
        "hi", "hello", "hey", "start", "help"
    ]

    def __init__(self):
        print("\n=== Initializing ChatService ===")
        self.auth_service = ChatAuthenticationService()
        self.menu_service = ChatMenuService()
        self.api_service = InstafinAPIService()

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

    @classmethod
    async def process_message(cls, session, message_content: str):
        """Process incoming message and return response"""
        print(f"\n=== Processing Message: '{message_content}' ===")
        service = cls()
        
        try:
            # Check if this is a greeting
            if message_content.lower() in cls.GREETING_MESSAGES:
                print("✅ Greeting detected, sending welcome message")
                return (
                    "Welcome to Instafin! 👋\n\n"
                    "To get started, please provide your account ID or account number."
                )

            # Check if message is a number (potential account ID)
            if message_content.isdigit():
                print(f"\n🔍 Validating account: {message_content}")
                return await service.handle_account_validation(session, message_content)
            
            # If not a number, check for FAQ matches
            print("\n🔍 Checking for FAQ match")
            faq_response = await service.check_faq(message_content)
            if faq_response:
                return faq_response
            
            # If authenticated, treat as menu selection
            if session.metadata.get('is_authenticated'):
                return await service._handle_authenticated_message(session, message_content)
            
            # Default response if no FAQ match and not authenticated
            return (
                "I couldn't understand that. Please provide a valid account number "
                "or ask me a question I can help you with."
            )
            
        except Exception as e:
            print(f"❌ Error in process_message: {str(e)}")
            return "I'm having trouble processing your message. Please try again."

    async def check_faq(self, message: str) -> Optional[str]:
        """Check if message matches any FAQ"""
        try:
            print(f"\n🔍 Checking FAQ match for: {message}")
            
            # Simple case-insensitive search in question field
            faq = await FAQ.objects.filter(
                question__icontains=message,
                is_active=True,
                is_public=True
            ).order_by('-priority').afirst()
            
            if faq:
                print(f"✅ Found matching FAQ: {faq.question[:50]}...")
                # Increment usage count
                await FAQ.objects.filter(id=faq.id).aupdate(usage_count=F('usage_count') + 1)
                return faq.answer
                
            print("❌ No matching FAQ found")
            return None
            
        except Exception as e:
            print(f"❌ Error checking FAQ: {str(e)}")
            return None

    async def handle_account_validation(self, session, account_id: str) -> str:
        """Handle account validation flow"""
        auth_data = await self.auth_service.authenticate_user(account_id)
        
        if auth_data:
            print("✅ Account validated successfully")
            session.metadata.update(auth_data)
            await session.asave()
            
            return (
                f"Welcome {auth_data.get('customer_name', 'valued customer')}! "
                "How can I help you today?\n\n"
                "1. View Loan Statement\n"
                "2. Check Repayment Schedule\n"
                "3. View Account Summary\n"
                "4. View Notifications\n\n"
                "Type 'help' for assistance or 'exit' to end session."
            )
        else:
            print("❌ Account validation failed")
            return (
                "I couldn't verify your account. "
                "Please provide a valid account ID or account number to get started."
            )

    async def _handle_authenticated_message(self, session, message_content: str):
        """Handle messages for authenticated sessions"""
        try:
            menu_response = await self.menu_service.handle_menu_selection(message_content)
            
            if menu_response['action'] == 'end_session':
                session.status = 'closed'
                session.ended_at = timezone.now()
                await session.asave()
                return menu_response['message']
                
            if menu_response['action'] == None:
                return menu_response['message']
                
            account_id = session.metadata.get('account_id')
            print(f"\nProcessing action {menu_response['action']} for account {account_id}")
            
            # Handle menu actions
            if menu_response['action'] == 'fetch_loan_statement':
                return await self.api_service.lookup_debts(account_id)
                
            elif menu_response['action'] == 'fetch_repayment_schedule':
                return "Repayment schedule feature coming soon!"
                
            elif menu_response['action'] == 'fetch_account_summary':
                return "Account summary feature coming soon!"
                
            elif menu_response['action'] == 'fetch_notifications':
                return "Notifications feature coming soon!"
                
        except Exception as e:
            print(f"❌ Error processing menu action: {str(e)}")
            return "Sorry, I encountered an error processing your request. Please try again."

        return menu_response['message']

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