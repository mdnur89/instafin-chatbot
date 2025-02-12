from django.conf import settings
from django.utils import timezone
from .models import Intent, Conversation, ConversationTurn, EntityType
from communications.services import AgentManagementService
from intelligence.services.knowledge_service import KnowledgeService
from .context import ConversationContextManager
import spacy
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .templates import ResponseTemplateManager

class ChatbotService:
    """Service for processing chatbot interactions"""
    
    def __init__(self):
        self.context_manager = ConversationContextManager()
        self.nlp = self._initialize_nlu()
        self.min_confidence = 0.7
        self.template_manager = ResponseTemplateManager()
        self.knowledge_service = KnowledgeService()
        
    def _initialize_nlu(self):
        """Initialize NLP model"""
        try:
            return spacy.load("en_core_web_md")
        except OSError:
            # If model not found, download it
            spacy.cli.download("en_core_web_md")
            return spacy.load("en_core_web_md")
    
    async def process_message(self, chat_session, message):
        """Process incoming message and generate response"""
        conversation = await self._get_or_create_conversation(chat_session)
        
        # First try to match with intents
        intent, confidence, entities = await self._process_nlu(message)
        
        # If confidence is low, try knowledge base
        if confidence < self.min_confidence:
            knowledge_results = await self.knowledge_service.find_relevant_knowledge(message)
            if knowledge_results:
                best_match = knowledge_results[0]
                if best_match['similarity'] > self.min_confidence:
                    return await self._format_knowledge_response(best_match['entry'])
        
        # Update context with entities
        await self.context_manager.update_context(
            conversation.id,
            {'entities': entities}
        )
        
        if confidence < self.min_confidence:
            return await self._handle_low_confidence(conversation, message)
            
        return await self._generate_response(conversation, intent, entities)
    
    async def _process_nlu(self, message):
        """Process message with NLU to extract intent and entities"""
        # Get all intents
        intents = await Intent.objects.all()
        
        # Process message with spaCy
        doc = self.nlp(message.lower())
        
        # Calculate similarity with each intent's training phrases
        max_similarity = 0
        matched_intent = None
        
        for intent in intents:
            for phrase in intent.training_phrases:
                phrase_doc = self.nlp(phrase.lower())
                similarity = doc.similarity(phrase_doc)
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    matched_intent = intent
        
        # Extract entities
        entities = {}
        for ent in doc.ents:
            entity_type = await EntityType.objects.filter(name=ent.label_).afirst()
            if entity_type:
                entities[entity_type.name] = ent.text
        
        return matched_intent, max_similarity, entities
    
    async def _generate_response(self, conversation, intent, entities):
        """Generate response based on intent and entities"""
        if not intent:
            return "I'm not sure I understand. Could you please rephrase that?"
        
        # Get context
        context = await self.context_manager.get_context(conversation.id)
        
        # Check if we have all required parameters
        missing_params = []
        for param in intent.required_parameters:
            if param not in entities and param not in context.get('entities', {}):
                missing_params.append(param)
        
        if missing_params:
            # Ask for missing parameter
            return f"Could you please provide the {missing_params[0]}?"
        
        # Get response template
        template = await self._get_response_template(intent)
        
        # Fill template with entities and context
        all_entities = {**context.get('entities', {}), **entities}
        response = await self._fill_template(template, all_entities)
        
        return response
    
    async def _handle_low_confidence(self, conversation, message):
        """Handle cases where intent confidence is low"""
        # Check if we should escalate to human agent
        if await self._should_escalate(conversation):
            agent = await AgentManagementService.find_available_agent()
            if agent:
                await AgentManagementService.track_chat_assignment(agent, 'add')
                return "I'll connect you with a human agent who can better assist you."
        
        return "I'm not quite sure I understand. Could you rephrase that?"
    
    async def _should_escalate(self, conversation):
        """Determine if conversation should be escalated to human agent"""
        # Get conversation turns
        turns = await ConversationTurn.objects.filter(
            conversation=conversation
        ).acount()
        
        # Escalate if:
        # 1. Too many low confidence turns
        # 2. User seems frustrated
        # 3. Complex query detected
        return turns >= 3
    
    async def _get_or_create_conversation(self, chat_session):
        """Get existing conversation or create new one"""
        conversation = await Conversation.objects.filter(
            chat_session=chat_session,
            status='active'
        ).afirst()
        
        if not conversation:
            conversation = await Conversation.objects.acreate(
                chat_session=chat_session,
                status='active',
                started_at=timezone.now()
            )
        
        return conversation
    
    async def _store_conversation_turn(self, conversation, user_message, 
                                     bot_response, intent, confidence, entities):
        """Store conversation turn in database"""
        await ConversationTurn.objects.acreate(
            conversation=conversation,
            user_message=user_message,
            bot_response=bot_response,
            intent=intent,
            confidence_score=confidence,
            parameters=entities,
            timestamp=timezone.now()
        )
    
    async def _get_response_template(self, intent):
        """Get appropriate response template for the intent"""
        return await self.template_manager.get_template(intent)
    
    async def _fill_template(self, template, entities):
        """Fill template with entity values"""
        return await self.template_manager.fill_template(template, entities)

    async def _format_knowledge_response(self, knowledge_entry):
        """Format knowledge base entry into a response"""
        # You might want to customize this based on your needs
        return f"{knowledge_entry.content}\n\nThis information is from our knowledge base about: {knowledge_entry.title}"

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