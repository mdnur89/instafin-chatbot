from .message_handlers import WhatsAppMessageHandler, FacebookMessageHandler
from communications.models import ChatSession
from intelligence.models import NLUModel, FAQ, KnowledgeBase

class ChatbotService:
    def __init__(self):
        self.model = None
        self.handlers = {
            'whatsapp': WhatsAppMessageHandler(),
            'facebook': FacebookMessageHandler()
        }
    
    async def get_model(self):
        if not self.model:
            self.model = await NLUModel.objects.filter(name="Test Model").afirst()
        return self.model

    async def process_message(self, session: ChatSession, message: str) -> str:
        handler = self.handlers.get(session.platform)
        if not handler:
            raise ValueError(f"Unsupported platform: {session.platform}")

        # Get the model and use it to process the message
        model = await self.get_model()
        if not model:
            return "Sorry, I'm not ready to help yet."

        # Use the model to find the best matching FAQ or Knowledge Base entry
        intent = await model.predict(message)  # You'll need to implement this
        
        # Find relevant response
        response = None
        if intent:
            # Try FAQ first
            faq = await FAQ.objects.filter(question__icontains=intent).afirst()
            if faq:
                response = faq.answer
            else:
                # Try Knowledge Base
                kb = await KnowledgeBase.objects.filter(
                    keywords__contains=[intent]
                ).afirst()
                if kb:
                    response = kb.content

        return response or "I'm sorry, I don't understand that question." 