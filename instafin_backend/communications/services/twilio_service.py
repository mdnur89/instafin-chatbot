from venv import logger
from twilio.rest import Client
from django.conf import settings
from ..models import PlatformMessage, PlatformIntegration
from ..services import ChatService
from django.core.exceptions import ValidationError
from twilio.base.exceptions import TwilioRestException

class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER

    async def send_message(self, to_number, message, media_url=None):
        """Send WhatsApp message via Twilio"""
        try:
            # Format WhatsApp number
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'

            # Get platform configuration
            platform = await self.get_platform()
            
            # Send message
            message_sid = await self._send_twilio_message(
                platform.config,
                to_number,
                message,
                media_url
            )
            
            return message_sid
        except TwilioRestException as e:
            logger.error(f"Twilio API error: {str(e)}")
            raise ValidationError(f"Failed to send WhatsApp message: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise ValidationError("An unexpected error occurred while sending the message")

    def get_chat_session(self, whatsapp_number):
        """Get or create chat session for WhatsApp number"""
        return ChatService.get_or_create_session(
            platform='whatsapp',
            external_id=whatsapp_number
        )

    @staticmethod
    async def get_platform():
        """Get or create Twilio WhatsApp platform integration"""
        platform, created = await PlatformIntegration.objects.aget_or_create(
            platform='whatsapp',
            defaults={
                'name': 'WhatsApp',
                'provider': 'twilio',
                'config': {
                    'account_sid': settings.TWILIO_ACCOUNT_SID,
                    'auth_token': settings.TWILIO_AUTH_TOKEN,
                    'phone_number': settings.TWILIO_WHATSAPP_NUMBER
                },
                'webhook_url': '/communications/webhooks/twilio/',
                'is_active': True
            }
        )
        return platform

    @staticmethod
    async def send_message(to_number, message):
        """Send WhatsApp message via Twilio"""
        try:
            platform = await TwilioService.get_platform()
            config = platform.config
            
            client = Client(config['account_sid'], config['auth_token'])
            
            message = await client.messages.create(
                from_=f"whatsapp:{config['phone_number']}",
                body=message,
                to=f"whatsapp:{to_number}"
            )
            
            return message.sid
            
        except Exception as e:
            raise ValidationError(f"Failed to send WhatsApp message: {str(e)}") 