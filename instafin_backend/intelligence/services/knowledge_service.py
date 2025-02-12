import spacy
import numpy as np
from django.conf import settings
from ..models import KnowledgeBase, NLUModel

class KnowledgeService:
    """Service for managing and training knowledge base"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_md")
    
    async def generate_embeddings(self, content: str) -> list:
        """Generate vector embeddings for content"""
        doc = self.nlp(content)
        return doc.vector.tolist()
    
    async def update_knowledge_embeddings(self):
        """Update embeddings for all active knowledge base entries"""
        async for entry in KnowledgeBase.objects.filter(is_active=True):
            entry.embeddings = await self.generate_embeddings(entry.content)
            await entry.asave()
    
    async def find_relevant_knowledge(self, query: str, threshold: float = 0.7) -> list:
        """Find relevant knowledge base entries for a query"""
        query_embedding = self.nlp(query).vector
        results = []
        
        async for entry in KnowledgeBase.objects.filter(is_active=True):
            if not entry.embeddings:
                continue
            
            similarity = np.dot(query_embedding, np.array(entry.embeddings))
            if similarity >= threshold:
                results.append({
                    'entry': entry,
                    'similarity': float(similarity)
                })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True) 