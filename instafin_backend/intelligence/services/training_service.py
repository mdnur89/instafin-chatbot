from django.db.models import Q
from ..models import FAQ, KnowledgeBase, NLUModel, TrainingSession
import spacy
import numpy as np
from datetime import datetime

class TrainingService:
    """Service for training NLU models on FAQs and Knowledge Base"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_md")
    
    async def train_model(self, model_id: int) -> dict:
        """Train NLU model on all available training data"""
        model = await NLUModel.objects.aget(id=model_id)
        session = await TrainingSession.objects.acreate(
            model=model,
            status='running'
        )
        
        try:
            # Collect training data
            training_data = await self._collect_training_data()
            
            # Generate embeddings for all training data
            embeddings = await self._generate_embeddings(training_data)
            
            # Update model configuration with new embeddings
            model.configuration['embeddings'] = embeddings
            model.is_training = False
            model.last_trained = datetime.now()
            await model.asave()
            
            # Update session status
            session.status = 'completed'
            session.metrics = {
                'training_samples': len(training_data),
                'completion_time': datetime.now().isoformat()
            }
            await session.asave()
            
            return {'status': 'success', 'samples_trained': len(training_data)}
            
        except Exception as e:
            session.status = 'failed'
            session.error_log = str(e)
            await session.asave()
            raise
    
    async def _collect_training_data(self):
        """Collect all training data from FAQs and Knowledge Base"""
        training_data = []
        
        # Collect FAQ training data
        async for faq in FAQ.objects.filter(is_training_data=True, is_active=True):
            training_data.append({
                'text': faq.question,
                'variations': faq.variations,
                'response': faq.answer,
                'type': 'faq'
            })
        
        # Collect Knowledge Base training data
        async for kb in KnowledgeBase.objects.filter(is_training_data=True, is_active=True):
            training_data.append({
                'text': kb.title,
                'variations': kb.keywords,
                'response': kb.content,
                'type': 'knowledge'
            })
        
        return training_data
    
    async def _generate_embeddings(self, training_data):
        """Generate embeddings for training data"""
        embeddings = {}
        for item in training_data:
            # Generate embeddings for main text
            doc = self.nlp(item['text'])
            main_vector = doc.vector.tolist()
            
            # Generate embeddings for variations
            variation_vectors = []
            for variation in item['variations']:
                var_doc = self.nlp(variation)
                variation_vectors.append(var_doc.vector.tolist())
            
            embeddings[item['text']] = {
                'main_vector': main_vector,
                'variation_vectors': variation_vectors,
                'response': item['response'],
                'type': item['type']
            }
        
        return embeddings 