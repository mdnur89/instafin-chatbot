from django import forms
from .models import Category, NLUModel, FAQ, TrainingSession, KnowledgeBase

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class NLUModelForm(forms.ModelForm):
    class Meta:
        model = NLUModel
        fields = ['name', 'description', 'model_type', 'version', 'configuration', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'configuration': forms.Textarea(attrs={'rows': 5, 'class': 'json-editor'}),
        }

    def clean_configuration(self):
        config = self.cleaned_data['configuration']
        # Add validation for required configuration fields based on model_type
        model_type = self.cleaned_data.get('model_type')
        if model_type == 'intent':
            required_fields = ['threshold', 'max_examples']
            for field in required_fields:
                if field not in config:
                    raise forms.ValidationError(f"Configuration must include {field} for intent models")
        return config

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'category', 'variations', 'priority',
                 'is_training_data', 'is_public', 'is_active']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 2}),
            'answer': forms.Textarea(attrs={'rows': 4}),
            'variations': forms.Textarea(attrs={'rows': 3, 'class': 'json-editor'}),
        }

    def clean_variations(self):
        variations = self.cleaned_data['variations']
        if not isinstance(variations, list):
            raise forms.ValidationError("Variations must be a list of strings")
        return variations

class TrainingSessionForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = ['model', 'status']
        widgets = {
            'status': forms.Select(choices=TrainingSession.status.field.choices)
        }

class KnowledgeBaseForm(forms.ModelForm):
    class Meta:
        model = KnowledgeBase
        fields = ['title', 'content', 'category', 'keywords', 'metadata',
                 'is_training_data', 'priority', 'is_active']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'keywords': forms.Textarea(attrs={'rows': 2, 'class': 'json-editor'}),
            'metadata': forms.Textarea(attrs={'rows': 3, 'class': 'json-editor'}),
        }

    def clean_keywords(self):
        keywords = self.cleaned_data['keywords']
        if not isinstance(keywords, list):
            raise forms.ValidationError("Keywords must be a list of strings")
        return keywords