from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from unittest.mock import Mock, patch
from chatbot.services.message_handlers import FacebookMessageHandler
from communications.models import ChatSession
from chat_platform.models import ChatPlatform, PlatformCredential
from twilio.base.exceptions import TwilioRestException

@override_settings(
    FACEBOOK_PAGE_ID='test_page_id',
    TWILIO_MESSAGING_SERVICE_SID='test_service_sid',
    FACEBOOK_VERIFY_TOKEN='test_verify_token',
    BUTTON_TEMPLATE_SID='test_button_template_sid',
)
class TestFacebookMessageHandler(TestCase):
    def setUp(self):
        # Create test user
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        # Create test platform and credentials
        self.platform = ChatPlatform.objects.create(
            name='FACEBOOK',
            is_active=True,
            api_base_url='https://test.twilio.com',
            api_version='v1'
        )
        self.credentials = PlatformCredential.objects.create(
            platform=self.platform,
            api_key='test_sid',
            api_secret='test_token'
        )
        
        # Create test chat session with user
        self.chat_session = ChatSession.objects.create(
            platform='facebook',
            user=self.user,
            metadata={
                'facebook_user_id': 'test_user_123'
            }
        )
        
        self.handler = FacebookMessageHandler()

    def create_mock_message(self, sid='test_message_sid'):
        mock_message = Mock()
        mock_message.sid = sid
        mock_message.status = 'sent'
        mock_message.error_code = None
        mock_message.error_message = None
        mock_message.message_id = sid  # Add message_id to mock
        return mock_message

    @patch('twilio.rest.Client')
    async def test_simple_text_message(self, mock_client_class):
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.return_value = self.create_mock_message()

        # Test sending a simple message
        response = await self.handler.process_message(
            self.chat_session,
            "Hello, test message"
        )
        
        # Verify Twilio was called correctly
        mock_client.messages.create.assert_called_with(
            from_='messenger:test_page_id',
            to='messenger:test_user_123',
            body="Hello, test message",
            messaging_service_sid='test_service_sid'
        )

    @patch('twilio.rest.Client')
    async def test_button_message(self, mock_client_class):
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.return_value = self.create_mock_message('test_button_sid')

        # Test sending a button message
        button_message = {
            "type": "button",
            "text": "Choose an option:",
            "buttons": [
                {"title": "Option 1", "payload": "opt1"},
                {"title": "Option 2", "payload": "opt2"}
            ]
        }
        
        response = await self.handler.process_message(
            self.chat_session,
            button_message
        )
        
        # Verify Twilio was called correctly
        mock_client.messages.create.assert_called_with(
            from_='messenger:test_page_id',
            to='messenger:test_user_123',
            content_sid='test_button_template_sid',
            messaging_service_sid='test_service_sid'
        )

    @patch('twilio.rest.Client')
    async def test_error_handling(self, mock_client):
        # Mock Twilio error
        mock_client.return_value.messages.create.side_effect = TwilioRestException(
            uri='test_uri',
            msg='Test error',
            code=123,
            status=400
        )

        # Test error handling
        with self.assertRaises(ValueError) as context:
            await self.handler.process_message(
                self.chat_session,
                "Test message"
            )
        
        self.assertIn('Failed to send Facebook message', str(context.exception))

    @patch('twilio.rest.Client')
    async def test_media_message(self, mock_client_class):
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.return_value = self.create_mock_message('test_media_sid')

        # Test sending a media message
        media_message = {
            "type": "media",
            "url": "https://example.com/image.jpg",
            "media_type": "image"
        }
        
        response = await self.handler.process_message(
            self.chat_session,
            media_message
        )
        
        # Verify Twilio was called correctly
        mock_client.messages.create.assert_called_with(
            from_='messenger:test_page_id',
            to='messenger:test_user_123',
            media_url=['https://example.com/image.jpg'],
            messaging_service_sid='test_service_sid'
        ) 