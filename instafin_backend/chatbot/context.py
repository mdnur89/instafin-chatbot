class ConversationContextManager:
    """Manages conversation context and state"""
    
    def __init__(self):
        self.context = {}
    
    async def update_context(self, conversation_id, updates):
        """Update context for a conversation"""
        if conversation_id not in self.context:
            self.context[conversation_id] = {}
        self.context[conversation_id].update(updates)
    
    async def get_context(self, conversation_id):
        """Get context for a conversation"""
        return self.context.get(conversation_id, {})
    
    async def clear_context(self, conversation_id):
        """Clear context for a conversation"""
        self.context.pop(conversation_id, None) 