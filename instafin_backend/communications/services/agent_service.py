from django.db.models import Q
from django.utils import timezone
from ..models import AgentAvailability, AgentPerformance

class AgentManagementService:
    """Service for managing agent availability and assignments"""

    @staticmethod
    async def update_agent_status(agent, status):
        """Update agent's availability status"""
        availability, _ = await AgentAvailability.objects.aget_or_create(
            agent=agent,
            defaults={'status': status}
        )
        availability.status = status
        availability.last_status_change = timezone.now()
        await availability.asave()
        return availability

    @staticmethod
    async def find_available_agent(skills_required=None):
        """Find the most suitable available agent based on skills and workload"""
        query = Q(status='available') & Q(auto_assign_enabled=True)
        query &= Q(current_chats__lt=models.F('max_concurrent_chats'))
        
        available_agents = AgentAvailability.objects.filter(query)
        
        if skills_required:
            available_agents = available_agents.filter(
                skills__contains=skills_required
            )
        
        return await available_agents.order_by('current_chats').afirst()

    @staticmethod
    async def track_chat_assignment(agent, action='add'):
        """Track chat assignment/removal for an agent"""
        availability = await AgentAvailability.objects.aget(agent=agent)
        
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
        
        await availability.asave()
        return availability

    @staticmethod
    async def update_performance_metrics(agent, date=None):
        """Update agent's performance metrics"""
        if date is None:
            date = timezone.now().date()
            
        # Get today's chats
        today_chats = await ChatSession.objects.filter(
            agent=agent,
            started_at__date=date
        ).acount()
        
        # Calculate metrics
        metrics = {
            'chats_handled': today_chats,
            'successful_resolutions': await ChatSession.objects.filter(
                agent=agent,
                started_at__date=date,
                status='closed'
            ).acount(),
            'avg_satisfaction': await ChatSession.objects.filter(
                agent=agent,
                started_at__date=date,
                satisfaction_score__isnull=False
            ).aaggregate(Avg('satisfaction_score'))
        }
        
        # Update or create performance record
        performance, _ = await AgentPerformance.objects.aupdate_or_create(
            agent=agent,
            date=date,
            defaults=metrics
        )
        return performance 