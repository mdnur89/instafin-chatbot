from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import ChatSession, ChatEscalation, ChatDocumentSubmission, AgentAvailability, AgentPerformance
from users.models import UserProfile

class ChatEscalationService:
    """Service to handle chat escalations to live agents"""
    
    @staticmethod
    def check_escalation_needed(chat_session):
        """Check if a chat needs to be escalated based on various factors"""
        # Check message count and duration
        message_count = chat_session.messages.count()
        duration = timezone.now() - chat_session.started_at
        
        # Get user profile and check for special handling
        user_profile = chat_session.user.profile
        
        conditions = [
            # Complex conversation
            message_count > 10 and duration.seconds > 300,
            # Minor user
            user_profile.is_minor(),
            # Negative sentiment detected
            chat_session.messages.filter(sentiment_score__lt=-0.5).exists(),
            # High value customer
            user_profile.account_tier in ['premium', 'vip'],
        ]
        
        if any(conditions):
            return True
        return False

    @staticmethod
    def assign_agent(escalation):
        """Assign the most suitable agent to handle the escalation"""
        available_agents = User.objects.filter(
            Q(is_staff=True) & 
            Q(is_active=True) & 
            ~Q(assigned_escalations__resolved_at=None)
        ).annotate(
            active_chats=Count('assigned_escalations', filter=Q(resolved_at=None))
        ).order_by('active_chats')
        
        if available_agents.exists():
            escalation.assigned_agent = available_agents.first()
            escalation.save()
            return True
        return False

class DocumentVerificationService:
    """Service to handle document verification through chat"""
    
    @staticmethod
    def process_document(submission):
        """Process and verify submitted documents"""
        # Implement document verification logic here
        # This could include:
        # 1. File type validation
        # 2. Virus scanning
        # 3. OCR processing
        # 4. Data extraction
        pass

    @staticmethod
    def notify_verification_result(submission):
        """Notify user about document verification result"""
        notification_data = {
            'type': 'document_verification',
            'status': submission.verification_status,
            'document_type': submission.document_type.name,
        }
        # Send notification to user
        pass

class AgentManagementService:
    """Service for managing agent availability and assignments"""
    
    @staticmethod
    def update_agent_status(agent, status):
        """Update agent's availability status"""
        availability, _ = AgentAvailability.objects.get_or_create(agent=agent)
        availability.status = status
        availability.last_status_change = timezone.now()
        availability.save()
        return availability

    @staticmethod
    def find_available_agent(skills_required=None):
        """Find the most suitable available agent based on skills and workload"""
        query = Q(status='available') & Q(auto_assign_enabled=True)
        query &= Q(current_chats__lt=models.F('max_concurrent_chats'))
        
        available_agents = AgentAvailability.objects.filter(query)
        
        if skills_required:
            # Filter agents with required skills
            available_agents = available_agents.filter(
                skills__contains=skills_required
            )
        
        # Order by workload (least busy first)
        return available_agents.order_by('current_chats').first()

    @staticmethod
    def track_chat_assignment(agent, action='add'):
        """Track chat assignment/removal for an agent"""
        availability = agent.availability
        if action == 'add':
            if availability.current_chats >= availability.max_concurrent_chats:
                raise ValidationError("Agent has reached maximum chat capacity")
            availability.current_chats += 1
            if availability.current_chats == availability.max_concurrent_chats:
                availability.status = 'busy'
        else:  # remove
            availability.current_chats = max(0, availability.current_chats - 1)
            if availability.status == 'busy' and availability.current_chats < availability.max_concurrent_chats:
                availability.status = 'available'
        availability.save()

    @staticmethod
    def update_performance_metrics(agent, date=None):
        """Update agent's performance metrics for a given date"""
        if date is None:
            date = timezone.now().date()
            
        # Get today's chats
        today_chats = ChatSession.objects.filter(
            agent=agent,
            started_at__date=date
        )
        
        # Calculate metrics
        metrics = {
            'chats_handled': today_chats.count(),
            'successful_resolutions': today_chats.filter(status='closed').count(),
            'escalated_chats': today_chats.filter(status='escalated').count(),
            'avg_satisfaction': today_chats.filter(
                satisfaction_score__isnull=False
            ).aggregate(Avg('satisfaction_score'))['satisfaction_score__avg']
        }
        
        # Update or create performance record
        performance, _ = AgentPerformance.objects.update_or_create(
            agent=agent,
            date=date,
            defaults=metrics
        )
        return performance 