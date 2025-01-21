from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Category, NLUModel, FAQ, TrainingSession
from .forms import CategoryForm, NLUModelForm, FAQForm, TrainingSessionForm

# Category Views
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'intelligence/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'intelligence/category_form.html'
    success_url = reverse_lazy('intelligence:category_list')

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'intelligence/category_form.html'
    success_url = reverse_lazy('intelligence:category_list')

# NLU Model Views
class NLUModelListView(LoginRequiredMixin, ListView):
    model = NLUModel
    template_name = 'intelligence/nlu_model_list.html'
    context_object_name = 'models'

class NLUModelCreateView(LoginRequiredMixin, CreateView):
    model = NLUModel
    form_class = NLUModelForm
    template_name = 'intelligence/nlu_model_form.html'
    success_url = reverse_lazy('intelligence:nlu_model_list')

class NLUModelUpdateView(LoginRequiredMixin, UpdateView):
    model = NLUModel
    form_class = NLUModelForm
    template_name = 'intelligence/nlu_model_form.html'
    success_url = reverse_lazy('intelligence:nlu_model_list')

class NLUModelDetailView(LoginRequiredMixin, DetailView):
    model = NLUModel
    template_name = 'intelligence/nlu_model_detail.html'
    context_object_name = 'model'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['training_sessions'] = TrainingSession.objects.filter(
            model=self.object
        ).order_by('-start_time')[:5]
        return context

# FAQ Views
class FAQListView(LoginRequiredMixin, ListView):
    model = FAQ
    template_name = 'intelligence/faq_list.html'
    context_object_name = 'faqs'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

class FAQCreateView(LoginRequiredMixin, CreateView):
    model = FAQ
    form_class = FAQForm
    template_name = 'intelligence/faq_form.html'
    success_url = reverse_lazy('intelligence:faq_list')

class FAQUpdateView(LoginRequiredMixin, UpdateView):
    model = FAQ
    form_class = FAQForm
    template_name = 'intelligence/faq_form.html'
    success_url = reverse_lazy('intelligence:faq_list')

# API Views for AJAX operations
def start_training(request, model_id):
    model = get_object_or_404(NLUModel, pk=model_id)
    if not model.is_training:
        session = TrainingSession.objects.create(
            model=model,
            status='pending'
        )
        # Here you would typically trigger your actual training process
        # For example, using Celery or similar
        return JsonResponse({'status': 'success', 'session_id': session.id})
    return JsonResponse({'status': 'error', 'message': 'Model is already training'})

def get_training_status(request, session_id):
    session = get_object_or_404(TrainingSession, pk=session_id)
    return JsonResponse({
        'status': session.status,
        'metrics': session.metrics,
        'error_log': session.error_log
    })
