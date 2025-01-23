from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date
from .models import AgeVerification, GuardianControl

class AgeVerificationService:
    """Service for managing age verification and parental controls"""
    
    @staticmethod
    def calculate_age(birth_date):
        """Calculate age from birth date"""
        today = date.today()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (
            today.month == birth_date.month and today.day < birth_date.day
        ):
            age -= 1
        return age

    @staticmethod
    def verify_age(user, date_of_birth, verification_document=None):
        """Verify user's age and set appropriate status"""
        age = AgeVerificationService.calculate_age(date_of_birth)
        
        verification, created = AgeVerification.objects.get_or_create(
            user=user,
            defaults={'date_of_birth': date_of_birth}
        )
        
        if age < 18:
            verification.verification_status = 'minor'
        else:
            verification.verification_status = 'verified'
            
        if verification_document:
            verification.verification_document = verification_document
            
        verification.verified_at = timezone.now()
        verification.save()
        return verification

class GuardianControlService:
    """Service for managing guardian controls and restrictions"""
    
    @staticmethod
    def setup_guardian_control(minor_user, guardian_user, daily_limit=None, restricted_features=None):
        """Set up guardian control for a minor user"""
        # Verify the guardian is not a minor
        guardian_verification = AgeVerification.objects.filter(
            user=guardian_user,
            verification_status='verified'
        ).first()
        
        if not guardian_verification:
            raise ValidationError("Guardian must be a verified adult user")
            
        # Create or update guardian control
        control, created = GuardianControl.objects.get_or_create(
            minor=minor_user,
            defaults={
                'guardian': guardian_user,
                'daily_transaction_limit': daily_limit,
                'restricted_features': restricted_features or []
            }
        )
        return control

    @staticmethod
    def check_transaction_allowed(minor_user, amount):
        """Check if a transaction is allowed for a minor user"""
        control = GuardianControl.objects.filter(minor=minor_user).first()
        if not control:
            raise ValidationError("No guardian control found for minor user")
            
        if control.daily_transaction_limit is None:
            return True
            
        # Get today's transactions
        today_start = timezone.now().replace(hour=0, minute=0, second=0)
        today_transactions = Transaction.objects.filter(
            user=minor_user,
            created_at__gte=today_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return (today_transactions + amount) <= control.daily_transaction_limit

    @staticmethod
    def notify_guardian(control, notification_type, **kwargs):
        """Send notification to guardian"""
        notification_data = {
            'recipient': control.guardian,
            'type': notification_type,
            'minor_user': control.minor.email,
            **kwargs
        }
        
        # Update last notification timestamp
        control.last_notification_sent = timezone.now()
        control.save()
        
        # Send notification (implement actual notification logic)
        return notification_data 