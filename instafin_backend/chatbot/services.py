from django.conf import settings
from .models import Intent, Conversation, ConversationTurn, EntityType
from communications.services import AgentManagementService

class ChatbotService:
    def __init__(self):
        self.nlu_processor = self._initialize_nlu()
        self.context_manager = ConversationContextManager()

    def _initialize_nlu(self):
        """Initialize NLU processor (placeholder for actual NLU implementation)"""
        # This would be replaced with actual NLU service
        # Could be spaCy, NLTK, or external service like Dialogflow
        return None

    async def process_message(self, chat_session, message_text):
        """Process incoming message and generate response"""
        # Get or create conversation
        conversation = await self._get_or_create_conversation(chat_session)

        # Detect intent
        intent_result = await self._detect_intent(message_text, conversation.context)
        
        # Update conversation with new intent
        conversation.current_intent = intent_result['intent']
        conversation.confidence_score = intent_result['confidence']
        
        # Check if human handoff is needed
        if self._needs_human_handoff(conversation, intent_result):
            return await self._handle_human_handoff(conversation)

        # Extract parameters
        params = await self._extract_parameters(
            message_text,
            conversation.current_intent,
            conversation.context
        )

        # Generate response
        response = await self._generate_response(conversation, params)

        # Save conversation turn
        await self._save_conversation_turn(
            conversation,
            message_text,
            response,
            intent_result,
            params
        )

        return response

    async def _detect_intent(self, message_text, context):
        """Detect intent from message"""
        # Placeholder for actual intent detection
        # This would use NLU service to detect intent
        return {
            'intent': None,
            'confidence': 0.0,
            'entities': {}
        }

    async def _extract_parameters(self, message_text, intent, context):
        """Extract parameters from message based on intent requirements"""
        # Placeholder for parameter extraction
        return {}

    async def _generate_response(self, conversation, params):
        """Generate appropriate response based on intent and parameters"""
        intent = conversation.current_intent
        if not intent:
            return "I'm not sure how to help with that. Could you please rephrase?"

        # Get response template
        template = self._get_response_template(intent, params)
        
        # Fill template with parameters
        response = self._fill_template(template, params, conversation.context)
        
        return response

    def _needs_human_handoff(self, conversation, intent_result):
        """Determine if conversation needs human handoff"""
        conditions = [
            conversation.confidence_score < settings.MIN_CONFIDENCE_THRESHOLD,
            conversation.current_intent and conversation.current_intent.requires_human,
            len(conversation.conversationturn_set.all()) > settings.MAX_TURNS_BEFORE_HANDOFF
        ]
        return any(conditions)

    async def _handle_human_handoff(self, conversation):
        """Handle handoff to human agent"""
        conversation.needs_human = True
        conversation.status = 'waiting_agent'
        await conversation.asave()

        # Find available agent
        agent = await AgentManagementService.find_available_agent()
        if agent:
            # Assign agent to chat session
            conversation.chat_session.agent = agent
            await conversation.chat_session.asave()
            return "I'm connecting you with a human agent who can better assist you."
        
        return "All our agents are currently busy. Please wait a moment."

class ConversationContextManager:
    """Manages conversation context and state"""

    def get_context(self, conversation_id):
        """Get current context for conversation"""
        conversation = Conversation.objects.get(id=conversation_id)
        return conversation.context

    def update_context(self, conversation_id, updates):
        """Update conversation context"""
        conversation = Conversation.objects.get(id=conversation_id)
        context = conversation.context
        context.update(updates)
        conversation.context = context
        conversation.save()

    def clear_context(self, conversation_id):
        """Clear conversation context"""
        conversation = Conversation.objects.get(id=conversation_id)
        conversation.context = {}
        conversation.save()