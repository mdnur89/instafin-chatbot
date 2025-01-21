# platforms/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import ChatPlatform, PlatformCredential, MessageTemplate, PlatformHealth
from .forms import PlatformForm, PlatformCredentialForm, MessageTemplateForm

class PlatformListView(LoginRequiredMixin, ListView):
    model = ChatPlatform
    template_name = 'chat_platforms/platform_list.html'
    context_object_name = 'platforms'

class PlatformDetailView(LoginRequiredMixin, DetailView):
    model = ChatPlatform
    template_name = 'chat_platforms/platform_detail.html'
    context_object_name = 'platform'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['health'] = self.object.health_logs.last()
        return context

class PlatformCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ChatPlatform
    form_class = PlatformForm
    template_name = 'chat_platforms/platform_form.html'
    success_url = reverse_lazy('platforms:platform_list')

    def test_func(self):
        return self.request.user.is_staff

class PlatformUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ChatPlatform
    form_class = PlatformForm
    template_name = 'chat_platforms/platform_form.html'

    def get_success_url(self):
        return reverse_lazy('platforms:platform_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        return self.request.user.is_staff

class PlatformDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ChatPlatform
    success_url = reverse_lazy('platforms:platform_list')
    
    def test_func(self):
        return self.request.user.is_staff

class PlatformHealthView(LoginRequiredMixin, TemplateView):
    template_name = 'chat_platforms/platform_health.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['platforms'] = ChatPlatform.objects.all()
        return context

class MessageTemplateListView(LoginRequiredMixin, ListView):
    model = MessageTemplate
    template_name = 'chat_platforms/template_list.html'
    context_object_name = 'templates'

    def get_queryset(self):
        queryset = super().get_queryset()
        platform = self.request.GET.get('platform')
        if platform:
            queryset = queryset.filter(platform__name=platform)
        return queryset

class MessageTemplateCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MessageTemplate
    form_class = MessageTemplateForm
    template_name = 'chat_platforms/template_form.html'
    success_url = reverse_lazy('platforms:template_list')

    def test_func(self):
        return self.request.user.is_staff

# API Views
class PlatformWebhookView(View):
    def post(self, request, platform):
        platform_obj = get_object_or_404(ChatPlatform, name=platform.upper())
        # Process webhook data
        return JsonResponse({'status': 'success'})

class TemplateAPIView(View):
    def get(self, request, platform):
        templates = MessageTemplate.objects.filter(
            platform__name=platform.upper(),
            is_active=True
        ).values('template_code', 'content', 'variables')
        return JsonResponse({'templates': list(templates)})