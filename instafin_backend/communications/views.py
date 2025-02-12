from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Prefetch, OuterRef, Subquery
from django.core.paginator import Paginator
from .models import (
    ChatSession, ChatMessage, NotificationTemplate, 
    Notification, SupportTicket, TicketResponse, PlatformMessage, PlatformIntegration
)
from .forms import (
    ChatMessageForm, NotificationTemplateForm, NotificationForm,
    SupportTicketForm, TicketResponseForm, BulkNotificationForm
)
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from typing import Tuple
from rest_framework.views import APIView
import logging
import time

logger = logging.getLogger(__name__)

# Create your views here.

# Chat Views
@login_required
def chat_session_list(request):
    sessions = ChatSession.objects.filter(
        Q(user=request.user) | Q(agent=request.user)
    ).select_related('user', 'agent').order_by('-started_at')
    
    paginator = Paginator(sessions, 20)
    page = request.GET.get('page')
    sessions = paginator.get_page(page)
    
    return render(request, 'communications/chat_session_list.html', {
        'sessions': sessions
    })

@login_required
def chat_session_detail(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id)
    messages = session.messages.select_related('sender').order_by('timestamp')
    form = ChatMessageForm()
    
    if request.method == 'POST':
        form = ChatMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.session = session
            message.sender = request.user
            message.save()
            return JsonResponse({
                'status': 'success',
                'message': {
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat(),
                    'sender': message.sender.get_full_name()
                }
            })
    
    return render(request, 'communications/chat_session_detail.html', {
        'session': session,
        'messages': messages,
        'form': form
    })

@login_required
def start_new_chat(request):
    # Get or create web platform
    platform = PlatformIntegration.objects.get(platform='web')
    
    # Create chat session
    session = ChatSession.objects.create(
        user=request.user,
        channel_type='general',
        status='active'
    )
    
    # Create platform message
    PlatformMessage.objects.create(
        platform=platform,
        chat_session=session,
        direction='in',
        content='Chat session started',
        external_id=f'web_{session.id}'
    )
    
    return redirect('communications:chat_session_detail', session_id=session.id)

# Notification Views
@staff_member_required
def notification_template_list(request):
    templates = NotificationTemplate.objects.all().order_by('-created_at')
    return render(request, 'communications/notification_template_list.html', {
        'templates': templates
    })

@staff_member_required
def notification_template_create(request):
    if request.method == 'POST':
        form = NotificationTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification template created successfully.')
            return redirect('communications:notification_template_list')
    else:
        form = NotificationTemplateForm()
    
    return render(request, 'communications/notification_template_form.html', {
        'form': form,
        'title': 'Create Notification Template'
    })

@staff_member_required
def send_bulk_notification(request):
    if request.method == 'POST':
        form = BulkNotificationForm(request.POST, user_choices=get_user_choices())
        if form.is_valid():
            template = form.cleaned_data['template']
            recipients = form.cleaned_data['recipients']
            scheduled_for = form.cleaned_data['scheduled_for']
            
            notifications = []
            for recipient_id in recipients:
                notifications.append(Notification(
                    recipient_id=recipient_id,
                    template=template,
                    title=template.subject,
                    message=template.content,
                    scheduled_for=scheduled_for
                ))
            
            Notification.objects.bulk_create(notifications)
            messages.success(request, f'Scheduled {len(notifications)} notifications.')
            return redirect('communications:notification_list')
    else:
        form = BulkNotificationForm(user_choices=get_user_choices())
    
    return render(request, 'communications/bulk_notification_form.html', {
        'form': form
    })

# Support Ticket Views
@login_required
def ticket_list(request):
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'communications/ticket_list.html', {
        'tickets': tickets
    })

@login_required
def ticket_detail(request, ticket_number):
    ticket = get_object_or_404(SupportTicket, ticket_number=ticket_number)
    responses = ticket.responses.select_related('responder').order_by('created_at')
    form = TicketResponseForm()
    
    if request.method == 'POST':
        form = TicketResponseForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.responder = request.user
            response.save()
            
            # Update ticket status
            if ticket.status == 'pending' and not request.user.is_staff:
                ticket.status = 'in_progress'
                ticket.save()
            
            messages.success(request, 'Response added successfully.')
            return redirect('communications:ticket_detail', ticket_number=ticket_number)
    
    return render(request, 'communications/ticket_detail.html', {
        'ticket': ticket,
        'responses': responses,
        'form': form
    })

@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, 'Support ticket created successfully.')
            return redirect('communications:ticket_detail', ticket_number=ticket.ticket_number)
    else:
        form = SupportTicketForm()
    
    return render(request, 'communications/ticket_form.html', {
        'form': form,
        'title': 'Create Support Ticket'
    })

# Utility Functions
def get_user_choices():
    User = get_user_model()
    return User.objects.filter(is_active=True).values_list('id', 'email')

class ChatSessionListView(ListView):
    model = ChatSession
    template_name = 'communications/chat_session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        # Get the last message for each chat session
        last_message = ChatMessage.objects.filter(
            session=OuterRef('pk')
        ).order_by('-timestamp')

        # Get the platform message for each chat session
        platform_message = PlatformMessage.objects.filter(
            chat_session=OuterRef('pk')
        ).select_related('platform').first()

        return ChatSession.objects.select_related('user').annotate(
            last_message=Subquery(
                last_message.values('content')[:1]
            ),
            platform_message=Subquery(
                platform_message.values('platform__platform')[:1]
            )
        ).order_by('-started_at')

class TwilioWebhookView(APIView):
    async def get_or_create_session(self, phone_number: str) -> Tuple[ChatSession, bool]:
        try:
            User = get_user_model()
            logger.info(f"Processing WhatsApp message from: {phone_number}")
            
            # First try to find existing user by phone number
            existing_user = await User.objects.filter(phone_number=phone_number).afirst()
            logger.info(f"Existing user found: {existing_user is not None}")
            
            if existing_user:
                user = existing_user
                logger.info(f"Using existing user with phone: {phone_number}")
            else:
                # Generate unique email with more entropy
                timestamp = int(time.time() * 1000)  # millisecond precision
                unique_suffix = get_random_string(16)  # increased from 8 to 16
                sanitized_phone = phone_number.replace('+', '').replace('-', '')
                unique_email = f"wa_{timestamp}_{unique_suffix}@chat.instafin.local"
                
                logger.info(f"Creating new user with email: {unique_email}")
                
                # Create user with try-except block
                try:
                    user = await User.objects.acreate(
                        phone_number=phone_number,
                        email=unique_email,
                        first_name=f'WhatsApp User',
                        last_name=sanitized_phone[-4:],
                        is_active=True
                    )
                    logger.info(f"Successfully created new user for phone: {phone_number}")
                except Exception as e:
                    logger.error(f"Failed to create user: {str(e)}")
                    raise
            
            # Get or create session
            session, created = await ChatSession.objects.aget_or_create(
                user=user,
                platform='whatsapp',
                defaults={
                    'channel_type': 'whatsapp',
                    'metadata': {'phone_number': phone_number}
                }
            )
            logger.info(f"Chat session {'created' if created else 'retrieved'} for phone: {phone_number}")
            
            return session, created
            
        except Exception as e:
            logger.error(f"Error in get_or_create_session: {str(e)}")
            raise

    async def post(self, request, *args, **kwargs):
        try:
            phone_number = request.data.get('From', '').split(':')[-1]  # Extract number from "whatsapp:+1234567890"
            message = request.data.get('Body', '')
            
            session, _ = await self.get_or_create_session(phone_number)
            
            # Process message logic here
            
            return JsonResponse({"status": "success"})
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return JsonResponse({"status": "error", "message": "Could not process message at this time"})
