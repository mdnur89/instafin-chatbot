from communications.services.chat_service import ChatService
from django.contrib.auth import get_user_model
from communications.models import ChatSession
import logging
import uuid
import sys

User = get_user_model()
logger = logging.getLogger(__name__)

class WebMessageHandler:
    """Handler for web-based chat messages"""

    def __init__(self):
        print("Initializing WebMessageHandler", file=sys.stderr)
        self.chat_service = ChatService()

    async def handle_message(self, message_content: str, session_id: str = None):
        """Process a message from the web interface"""
        print(f"\n=== Processing web message: {message_content} ===", file=sys.stderr)
        try:
            # Create or get user for web session
            email = f"web_{session_id}@webchat.local"
            user = await User.objects.filter(email=email).afirst()
            if not user:
                user = await User.objects.acreate(
                    email=email,
                    first_name="Web User",
                    last_name=session_id[:8],
                    is_active=True,
                    is_verified=False,
                    phone_number=f"web_{session_id}"
                )

            # Get or create chat session
            session = await ChatSession.objects.filter(
                platform='web',
                user=user,
                status='active'
            ).afirst()

            if not session:
                session = await ChatSession.objects.acreate(
                    platform='web',
                    user=user,
                    channel_type='general',
                    status='active',
                    metadata={'web_session_id': session_id}
                )

            # Process message and get response
            print("Processing message through ChatService", file=sys.stderr)
            response = await self.chat_service.process_message(
                session=session,
                message_content=message_content
            )
            print(f"ChatService response: {response}", file=sys.stderr)

            return response

        except Exception as e:
            print(f"Error in handle_message: {str(e)}", file=sys.stderr)
            logger.exception("Error processing web message")
            raise 