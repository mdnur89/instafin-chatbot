from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import Intent, Conversation, ConversationTurn
from .services import ChatbotService
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import traceback
from communications.models import ChatSession
import logging
from asgiref.sync import async_to_sync
import uuid
from .handlers.web_handler import WebMessageHandler

logger = logging.getLogger(__name__)

# Create your views here.

class ChatWidgetView(TemplateView):
    """View for rendering the chat widget interface"""
    template_name = 'chatbot/chat_widget.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data needed for the chat widget
        return context

def log_event(message):
    """Force print to terminal"""
    print(f"\n[CHATBOT EVENT] {message}", file=sys.stderr, flush=True)

@csrf_exempt
async def chat_message(request):
    log_event("=== New Chat Request ===")
    
    if request.method == 'POST':
        try:
            log_event("Received POST request")
            data = json.loads(request.body)
            message = data.get('message', '')
            log_event(f"User message: {message}")
            
            # Create a web handler instance
            handler = WebMessageHandler()
            
            # Generate a session ID from the request if not provided
            session_id = request.session.session_key or str(uuid.uuid4())
            
            # Process the message
            response = await handler.handle_message(
                message_content=message,
                session_id=session_id
            )
            
            return JsonResponse({
                'type': 'bot_response',
                'message': response
            })
            
        except Exception as e:
            log_event(f"ERROR: {str(e)}")
            return JsonResponse({
                'type': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
