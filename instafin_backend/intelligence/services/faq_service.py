from typing import List, Dict, Optional
from django.db.models import F
from ..models import FAQ
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class FAQMatchingService:
    """Service for matching user queries to FAQs"""

    @staticmethod
    async def find_matching_faq(query: str, threshold: float = 0.7) -> Optional[Dict]:
        """Find the best matching FAQ for a given query"""
        best_match = None
        best_ratio = 0

        async for faq in FAQ.objects.filter(is_active=True, is_public=True):
            ratio = SequenceMatcher(None, query.lower(), faq.question.lower()).ratio()
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = faq

        if best_match:
            await FAQ.objects.filter(id=best_match.id).aupdate(usage_count=F('usage_count') + 1)
            return {
                'question': best_match.question,
                'answer': best_match.answer,
                'confidence': best_ratio
            }
        return None 