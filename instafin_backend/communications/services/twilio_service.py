from twilio.rest import Client
from django.conf import settings
from ..models import PlatformMessage, PlatformIntegration
from ..services import ChatService

class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER

    def send_message(self, to_number, message, media_url=None):
        """Send WhatsApp message via Twilio"""
        try:
            # Ensure number is in WhatsApp format
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'

            # Prepare message data
            message_data = {
                'from_': self.whatsapp_number,
                'to': to_number,
                'body': message
            }

            # Add media if provided
            if media_url:
                message_data['media_url'] = [media_url]

            # Send message
            twilio_message = self.client.messages.create(**message_data)

            # Store message in our database
            platform = PlatformIntegration.objects.get(platform='whatsapp')
            stored_message = PlatformMessage.objects.create(
                platform=platform,
                external_id=twilio_message.sid,
                chat_session=self.get_chat_session(to_number),
                direction='out',
                content=message,
                metadata={
                    'media_url': media_url,
                    'whatsapp_number': to_number,
                    'status': twilio_message.status
                }
            )

            return stored_message

        except Exception as e:
            logger.error(f"Error sending Twilio message: {str(e)}")
            raise

    def get_chat_session(self, whatsapp_number):
        """Get or create chat session for WhatsApp number"""
        return ChatService.get_or_create_session(
            platform='whatsapp',
            external_id=whatsapp_number
        ) 