from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
import difflib

class Category(models.Model):
    """Categories for organizing FAQs and NLU intents"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class NLUModel(models.Model):
    """Configuration for different NLU models"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    model_type = models.CharField(max_length=50, choices=[
        ('intent', 'Intent Classification'),
        ('entity', 'Entity Recognition'),
        ('sentiment', 'Sentiment Analysis'),
        ('combined', 'Combined Model')
    ])
    version = models.CharField(max_length=20)
    configuration = models.JSONField(help_text="Model-specific configuration parameters")
    performance_metrics = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    is_training = models.BooleanField(default=False)
    last_trained = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    async def predict(self, text: str) -> str:
        """
        Predict the intent of the given text by finding the most similar FAQ question
        or Knowledge Base title using difflib's SequenceMatcher
        """
        # Get all FAQs and Knowledge Base entries marked as training data
        faqs = await FAQ.objects.filter(is_training_data=True).values_list('question', flat=True)
        kb_entries = await KnowledgeBase.objects.filter(is_training_data=True).values_list('title', flat=True)
        
        # Combine all training texts
        training_texts = list(faqs) + list(kb_entries)
        
        if not training_texts:
            return None
            
        # Find the best match using sequence matching
        best_match = None
        highest_ratio = 0
        
        for training_text in training_texts:
            ratio = difflib.SequenceMatcher(None, text.lower(), training_text.lower()).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = training_text
        
        # Only return a match if it's reasonably similar (threshold of 0.5)
        return best_match if highest_ratio > 0.5 else None

    def __str__(self):
        return f"{self.name} v{self.version}"

class FAQ(models.Model):
    """Frequently Asked Questions"""
    question = models.TextField()
    answer = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    variations = models.JSONField(default=list, help_text="Alternative phrasings of the question")
    priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1-10 scale, higher number means higher priority"
    )
    is_training_data = models.BooleanField(
        default=True,
        help_text="Use this FAQ for training NLU models"
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Show this FAQ to users"
    )
    usage_count = models.IntegerField(default=0, help_text="Number of times this FAQ was used")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['-priority', '-usage_count']

    def __str__(self):
        return self.question[:100]

class TrainingSession(models.Model):
    """Track NLU model training sessions"""
    model = models.ForeignKey(NLUModel, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    metrics = models.JSONField(default=dict, blank=True)
    error_log = models.TextField(blank=True)

    def __str__(self):
        return f"{self.model.name} - {self.start_time}"

class KnowledgeBase(models.Model):
    """Company knowledge and information for chatbot training"""
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Main content/information")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    keywords = models.JSONField(
        default=list,
        help_text="Key terms or phrases related to this content"
    )
    embeddings = models.JSONField(
        null=True,
        blank=True,
        help_text="Vector embeddings of the content for semantic search"
    )
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata about the content"
    )
    is_training_data = models.BooleanField(
        default=True,
        help_text="Use this content for training NLU models"
    )
    priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1-10 scale, higher number means higher priority"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Knowledge Base Entry"
        verbose_name_plural = "Knowledge Base Entries"
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.title
