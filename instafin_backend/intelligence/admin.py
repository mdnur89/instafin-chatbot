from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, NLUModel, FAQ, TrainingSession, KnowledgeBase

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    compressed_fields = []

@admin.register(NLUModel)
class NLUModelAdmin(ModelAdmin):
    list_display = ('name', 'model_type', 'version', 'is_active', 'is_training', 'last_trained')
    list_filter = ('model_type', 'is_active', 'is_training')
    search_fields = ('name', 'description')
    readonly_fields = ('performance_metrics', 'last_trained')
    compressed_fields = []

@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ('question_preview', 'category', 'priority', 'is_training_data', 
                   'is_public', 'usage_count', 'is_active')
    list_filter = ('category', 'is_training_data', 'is_public', 'is_active')
    search_fields = ('question', 'answer')
    readonly_fields = ('usage_count',)
    compressed_fields = []

    def question_preview(self, obj):
        return obj.question[:100] + "..." if len(obj.question) > 100 else obj.question
    question_preview.short_description = 'Question'

@admin.register(TrainingSession)
class TrainingSessionAdmin(ModelAdmin):
    list_display = ('model', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'model')
    readonly_fields = ('start_time', 'end_time', 'metrics', 'error_log')
    compressed_fields = []

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(ModelAdmin):
    list_display = ('title', 'category', 'priority', 'is_training_data', 'is_active')
    list_filter = ('category', 'is_training_data', 'is_active')
    search_fields = ('title', 'content', 'keywords')
    readonly_fields = ('embeddings',)
    compressed_fields = []
