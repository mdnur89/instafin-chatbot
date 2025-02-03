from typing import List, Dict, Optional
from django.db.models import F
from .models import FAQ
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class FAQMatchingService:
    """Service for matching user queries to FAQs"""

    @staticmethod
    async def find_matching_faq(query: str, threshold: float = 0.7) -> Optional[Dict]:
        """
        Find the best matching FAQ for a given query
        
        Args:
            query: The user's question
            threshold: Minimum similarity score (0-1) to consider a match
            
        Returns:
            Dict containing the matched FAQ data or None if no match found
        """
        try:
            # Get active and public FAQs - using async query properly
            faqs = [faq async for faq in FAQ.objects.filter(
                is_active=True,
                is_public=True
            ).order_by('-priority')]

            best_match = None
            best_score = 0

            for faq in faqs:
                # Check main question
                score = SequenceMatcher(None, query.lower(), faq.question.lower()).ratio()
                
                # Check variations
                for variation in faq.variations:
                    var_score = SequenceMatcher(None, query.lower(), variation.lower()).ratio()
                    score = max(score, var_score)
                
                # Apply priority weighting
                priority_boost = (faq.priority - 1) * 0.02
                score += priority_boost

                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = faq

            if best_match:
                # Increment usage count
                await FAQ.objects.filter(id=best_match.id).aupdate(
                    usage_count=F('usage_count') + 1
                )
                
                return {
                    'answer': best_match.answer,
                    'confidence': best_score,
                    'faq_id': best_match.id
                }

            return None

        except Exception as e:
            logger.error(f"Error matching FAQ: {str(e)}")
            return None

    @staticmethod
    async def get_category_faqs(category_id: int) -> List[Dict]:
        """Get all FAQs for a specific category"""
        try:
            faqs = [faq async for faq in FAQ.objects.filter(
                category_id=category_id,
                is_active=True,
                is_public=True
            ).order_by('-priority')]
            return [
                {
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer,
                    'priority': faq.priority
                }
                for faq in faqs
            ]
        except Exception as e:
            logger.error(f"Error getting category FAQs: {str(e)}")
            return []