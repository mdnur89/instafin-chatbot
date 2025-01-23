from django.conf import settings
from django.core.exceptions import ValidationError
from ..models import PlatformIntegration
import requests
import json

class PlatformIntegrationService:
    """Service for managing platform integrations"""

    @staticmethod
    async def verify_credentials(platform):
        """Verify platform credentials are valid"""
        try:
            if platform.platform == 'whatsapp':
                return await PlatformIntegrationService._verify_twilio_credentials(platform)
            # Add other platform verifications here
            return False
        except Exception as e:
            platform.last_health_check = timezone.now()
            await platform.asave()
            raise ValidationError(f"Failed to verify credentials: {str(e)}")

    @staticmethod
    async def test_webhook(platform):
        """Test platform webhook configuration"""
        try:
            if not platform.webhook_url:
                raise ValidationError("No webhook URL configured")

            # Send test payload
            test_payload = {
                'test': True,
                'platform': platform.platform,
                'timestamp': timezone.now().isoformat()
            }

            response = await PlatformIntegrationService._send_webhook_request(
                platform.webhook_url,
                test_payload,
                platform.webhook_secret
            )

            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response': response.text
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    async def _verify_twilio_credentials(platform):
        """Verify Twilio credentials"""
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException

        config = platform.config
        try:
            client = Client(config.get('account_sid'), config.get('auth_token'))
            # Try to fetch account info to verify credentials
            account = client.api.accounts(config.get('account_sid')).fetch()
            
            platform.last_health_check = timezone.now()
            await platform.asave()
            
            return True
        except TwilioRestException:
            return False

    @staticmethod
    async def _send_webhook_request(url, payload, secret=None):
        """Send webhook request with optional signature"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        if secret:
            # Add signature if secret is provided
            timestamp = str(int(timezone.now().timestamp()))
            signature = PlatformIntegrationService._generate_signature(
                payload,
                timestamp,
                secret
            )
            headers.update({
                'X-Webhook-Signature': signature,
                'X-Webhook-Timestamp': timestamp
            })

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers
            )
            return response

    @staticmethod
    def _generate_signature(payload, timestamp, secret):
        """Generate webhook signature"""
        import hmac
        import hashlib

        message = f"{timestamp}.{json.dumps(payload)}"
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature 