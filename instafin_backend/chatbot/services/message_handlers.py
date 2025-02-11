from abc import ABC, abstractmethod
from ..models import Conversation
from communications.models import ChatSession
from chat_platform.models import PlatformMessage, ChatPlatform, PlatformCredential
import aiohttp
from typing import Dict, Any, Union
from django.conf import settings
from chat_platform.models import PlatformHealth
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from asgiref.sync import sync_to_async

class BaseMessageHandler(ABC):
    @abstractmethod
    async def process_message(self, session, message: str) -> str:
        pass

class WhatsAppMessageHandler(BaseMessageHandler):
    async def process_message(self, session: ChatSession, message: str) -> str:
        # Move existing WhatsApp-specific logic here
        # This can be copied from your current ChatbotService
        pass

class FacebookMessageHandler(BaseMessageHandler):
    async def get_twilio_client(self) -> Client:
        platform = await ChatPlatform.objects.aget(
            name='FACEBOOK',
            is_active=True
        )
        credentials = await PlatformCredential.objects.aget(platform=platform)
        
        return Client(
            credentials.api_key,  # Twilio Account SID
            credentials.api_secret  # Twilio Auth Token
        )

    @sync_to_async
    def send_twilio_message(
        self, 
        client: Client, 
        to: str, 
        content: Union[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        try:
            # Handle different message types
            if isinstance(content, str):
                # Simple text message
                response = client.messages.create(
                    from_=f'messenger:{settings.FACEBOOK_PAGE_ID}',
                    to=f'messenger:{to}',
                    body=content,
                    messaging_service_sid=settings.TWILIO_MESSAGING_SERVICE_SID
                )
            else:
                # Rich media message (template, buttons, etc.)
                media_url = content.get('media_url')
                template = content.get('template')
                buttons = content.get('buttons')

                message_params = {
                    'from_': f'messenger:{settings.FACEBOOK_PAGE_ID}',
                    'to': f'messenger:{to}',
                    'messaging_service_sid': settings.TWILIO_MESSAGING_SERVICE_SID
                }

                if media_url:
                    message_params['media_url'] = [media_url]
                
                if template:
                    # Handle Facebook template messages
                    message_params['content_sid'] = template['sid']
                    message_params['content_variables'] = template['variables']
                
                if buttons:
                    # Handle Facebook button template
                    message_params['content_sid'] = settings.BUTTON_TEMPLATE_SID
                    message_params['content_variables'] = {
                        'buttons': buttons
                    }

                response = client.messages.create(**message_params)

            return {
                'message_id': response.sid,
                'status': response.status,
                'error_code': response.error_code,
                'error_message': response.error_message
            }
        except TwilioRestException as e:
            raise ValueError(f"Twilio API error: {str(e)}")

    async def send_template_message(
        self, 
        session: ChatSession, 
        template_name: str, 
        variables: Dict[str, Any]
    ) -> str:
        """Send a template message"""
        client = await self.get_twilio_client()
        facebook_user_id = session.metadata.get('facebook_user_id')
        
        content = {
            'template': {
                'sid': template_name,
                'variables': variables
            }
        }
        
        return await self.send_twilio_message(client, facebook_user_id, content)

    async def send_button_message(
        self, 
        session: ChatSession, 
        text: str, 
        buttons: list
    ) -> str:
        """Send a message with buttons"""
        client = await self.get_twilio_client()
        facebook_user_id = session.metadata.get('facebook_user_id')
        
        content = {
            'buttons': {
                'text': text,
                'buttons': buttons
            }
        }
        
        return await self.send_twilio_message(client, facebook_user_id, content)

    async def send_media_message(
        self, 
        session: ChatSession, 
        media_url: str, 
        caption: str = None
    ) -> str:
        """Send a media message"""
        client = await self.get_twilio_client()
        facebook_user_id = session.metadata.get('facebook_user_id')
        
        content = {
            'media_url': media_url,
            'body': caption
        }
        
        return await self.send_twilio_message(client, facebook_user_id, content)

    async def process_message(self, session: ChatSession, message: Union[str, Dict[str, Any]]) -> str:
        try:
            # Send message based on type
            if isinstance(message, str):
                response = await self.send_twilio_message(
                    client=await self.get_twilio_client(),
                    to=session.metadata.get('facebook_user_id'),
                    content=message
                )
            else:
                # Handle rich media messages
                if message.get('template'):
                    response = await self.send_template_message(
                        session,
                        message['template']['name'],
                        message['template']['variables']
                    )
                elif message.get('buttons'):
                    response = await self.send_button_message(
                        session,
                        message['buttons']['text'],
                        message['buttons']['buttons']
                    )
                elif message.get('media_url'):
                    response = await self.send_media_message(
                        session,
                        message['media_url'],
                        message.get('caption')
                    )

            # Get platform for logging
            platform = await ChatPlatform.objects.aget(name='FACEBOOK', is_active=True)

            # Record the platform message
            await PlatformMessage.objects.acreate(
                platform=platform,
                external_id=response['message_id'],
                chat_session=session,
                direction='out',
                content=message,
                metadata={
                    'twilio_response': response,
                    'delivery_status': response['status']
                }
            )

            # Update platform health metrics
            await PlatformHealth.objects.acreate(
                platform=platform,
                status='UP' if response['status'] == 'delivered' else 'DEGRADED',
                response_time=0,  # Twilio doesn't provide this
                success_rate=100.0 if response['status'] == 'delivered' else 0.0,
                messages_sent=1,
                messages_failed=0 if response['status'] == 'delivered' else 1,
                additional_metrics={'twilio_status': response['status']}
            )

            return message

        except Exception as e:
            platform = await ChatPlatform.objects.aget(name='FACEBOOK', is_active=True)
            await PlatformHealth.objects.acreate(
                platform=platform,
                status='DEGRADED',
                response_time=0,
                success_rate=0.0,
                messages_sent=0,
                messages_failed=1,
                error_count=1,
                additional_metrics={'error': str(e)}
            )
            raise ValueError(f"Failed to send Facebook message via Twilio: {str(e)}") 