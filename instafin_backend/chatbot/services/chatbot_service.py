from .message_handlers import WhatsAppMessageHandler, FacebookMessageHandler
from communications.models import ChatSession

class ChatbotService:
    def __init__(self):
        self.handlers = {
            'whatsapp': WhatsAppMessageHandler(),
            'facebook': FacebookMessageHandler()
        }
    
    async def process_message(self, session: ChatSession, message: str) -> str:
        handler = self.handlers.get(session.platform)
        if not handler:
            raise ValueError(f"Unsupported platform: {session.platform}")
        return await handler.process_message(session, message) 