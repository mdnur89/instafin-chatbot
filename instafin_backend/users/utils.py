from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import User, UserCommunication, UserFeedback

def dashboard_callback(request, context):
    # Get general user statistics
    total_users = User.objects.count()
    verified_users = User.objects.filter(is_verified=True).count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Get recent communications
    recent_communications = UserCommunication.objects.filter(
        sent_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Get average credit score
    avg_credit_score = User.objects.filter(
        credit_score__isnull=False
    ).aggregate(Avg('credit_score'))['credit_score__avg']
    
    # Get feedback statistics
    feedback_stats = UserFeedback.objects.aggregate(
        avg_rating=Avg('rating'),
        total_feedback=Count('id')
    )
    
    context.update({
        "stats": {
            "total_users": total_users,
            "verified_users": verified_users,
            "active_users": active_users,
            "recent_communications": recent_communications,
            "avg_credit_score": round(avg_credit_score, 2) if avg_credit_score else 0,
            "avg_rating": round(feedback_stats['avg_rating'], 2) if feedback_stats['avg_rating'] else 0,
            "total_feedback": feedback_stats['total_feedback'],
        }
    })
    return context