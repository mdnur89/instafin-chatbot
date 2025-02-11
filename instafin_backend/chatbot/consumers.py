import json
import logging
import sys
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .services import ChatbotService
from chat_platform.models import ChatPlatform, PlatformMessage
from communications.models import ChatSession
from .handlers.web_message_handler import WebMessageHandler

# Force logging to stdout/stderr
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class ChatbotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            print("Initializing WebSocket connection...", file=sys.stderr)
            self.handler = WebMessageHandler()
            self.session_id = f"web_{self.scope['client'][0]}"
            await self.accept()
            print(f"WebSocket connected with session_id: {self.session_id}", file=sys.stderr)
        except Exception as e:
            print(f"Error in connect: {str(e)}", file=sys.stderr)
            raise

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        logger.info(f"WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        print(f"Received message: {text_data}", file=sys.stderr)
        try:
            # Parse incoming message
            data = json.loads(text_data)
            message = data.get('message', '')
            print(f"Processing message: {message}", file=sys.stderr)
            
            # Process message using handler
            response = await self.handler.handle_message(
                message_content=message,
                session_id=self.session_id
            )
            print(f"Handler response: {response}", file=sys.stderr)

            # Send response back to client
            await self.send(text_data=json.dumps({
                'type': 'bot_response',
                'message': response or "I'm sorry, I couldn't process that message."
            }))

        except Exception as e:
            print(f"Error in receive: {str(e)}", file=sys.stderr)
            logger.exception("Error processing message")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error: {str(e)}'  # More detailed error for debugging
            }))

    @database_sync_to_async
    def get_web_platform(self):
        platform, created = ChatPlatform.objects.get_or_create(
            name='WEB',
            defaults={'display_name': 'Website Chat', 'is_active': True}
        )
        print(f"Platform {'created' if created else 'retrieved'}: {platform}", file=sys.stderr)
        return platform

    @database_sync_to_async
    def create_chat_session(self):
        session = ChatSession.objects.create(
            platform=self.platform,
            session_id=f"web_{self.scope['client'][0]}",
            status='ACTIVE'
        )
        print(f"Chat session created with ID: {session.id}", file=sys.stderr)
        return session

    @database_sync_to_async
    def process_message_sync(self, message):
        print(f"Processing message: '{message}'", file=sys.stderr)
        try:
            # This should use the same logic as WhatsApp
            response = self.chatbot_service.process_message(
                self.chat_session,
                message
            )
            print(f"Response generated: '{response}'", file=sys.stderr)
            return response
        except Exception as e:
            print(f"Error processing message: {str(e)}", file=sys.stderr)
            logger.exception("Error processing message")
            return "Sorry, I encountered an error processing your message." 