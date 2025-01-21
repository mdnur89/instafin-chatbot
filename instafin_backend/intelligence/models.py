from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
    description = models.TextField()
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
