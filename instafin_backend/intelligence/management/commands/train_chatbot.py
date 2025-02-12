from django.core.management.base import BaseCommand
from intelligence.models import FAQ, KnowledgeBase, NLUModel, Category
from intelligence.services import TrainingService
from chatbot.services import ChatbotService
from communications.models import ChatSession
from django.contrib.auth import get_user_model
import asyncio

class Command(BaseCommand):
    help = 'Train chatbot with dummy data'

    def handle(self, *args, **kwargs):
        """Run the command synchronously"""
        asyncio.run(self.async_handle(*args, **kwargs))

    async def async_handle(self, *args, **kwargs):
        """Async implementation of the command"""
        self.stdout.write('Creating dummy data and training model...')
        
        # Get or create category
        category, created = await Category.objects.aget_or_create(
            name="Company Info",
            defaults={'description': 'General company information'}
        )

        # Create FAQs
        await FAQ.objects.aget_or_create(
            question="What is Instafin?",
            defaults={
                'answer': "Instafin is a financial technology company providing innovative solutions.",
                'category': category,
                'variations': ["Tell me about Instafin", "What does Instafin do?"],
                'is_training_data': True
            }
        )

        await FAQ.objects.aget_or_create(
            question="How can I contact support?",
            defaults={
                'answer': "You can reach our support team at support@instafin.com or call 1-800-INSTAFIN",
                'category': category,
                'variations': ["Contact information", "Support contact"],
                'is_training_data': True
            }
        )

        # Create Knowledge Base entries
        await KnowledgeBase.objects.aget_or_create(
            title="Company Mission",
            defaults={
                'content': "Our mission is to democratize financial services through technology.",
                'category': category,
                'keywords': ["mission", "vision", "values"],
                'is_training_data': True
            }
        )

        await KnowledgeBase.objects.aget_or_create(
            title="Product Overview",
            defaults={
                'content': "Instafin offers digital banking, investment management, and financial planning tools.",
                'category': category,
                'keywords': ["products", "services", "offerings"],
                'is_training_data': True
            }
        )

        # Create or get test model
        model, _ = await NLUModel.objects.aget_or_create(
            name="Test Model",
            defaults={
                'description': "Test model for company information",
                'configuration': {}
            }
        )

        # Train the model
        training_service = TrainingService()
        result = await training_service.train_model(model.id)
        self.stdout.write(self.style.SUCCESS(f'Training completed: {result}'))

        # Create or get test user
        User = get_user_model()
        test_user, _ = await User.objects.aget_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True
            }
        )

        # Create a test chat session
        test_session = await ChatSession.objects.acreate(
            platform='whatsapp',
            user=test_user,
            channel_type='general',
            metadata={'test': True}
        )

        # Test the chatbot
        chatbot = ChatbotService()
        response1 = await chatbot.process_message(test_session, "What is Instafin's mission?")
        response2 = await chatbot.process_message(test_session, "How do I contact support?")
        
        self.stdout.write("\nTest Results:")
        self.stdout.write(f"Q: What is Instafin's mission?\nA: {response1}")
        self.stdout.write(f"Q: How do I contact support?\nA: {response2}") 