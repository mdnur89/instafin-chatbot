from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from .models import (
    ChatSession, ChatMessage, NotificationTemplate, 
    Notification, SupportTicket, TicketResponse
)
from .forms import (
    ChatMessageForm, NotificationTemplateForm, NotificationForm,
    SupportTicketForm, TicketResponseForm, BulkNotificationForm
)

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
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.filter(is_active=True).values_list('id', 'email')
