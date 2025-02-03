from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from django.conf import settings
from ..models import PlatformMessage, PlatformIntegration
from ..services.chat_service import ChatService
from ..services import TwilioService

class TwilioWebhookHandler:
    def __init__(self):
        self.validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)

    def validate_request(self, request):
        """Validate that the request is from Twilio"""
        signature = request.headers.get('X-Twilio-Signature', '')
        url = request.build_absolute_uri()
        
        # Handle both GET and POST data
        if request.method == 'POST':
            params = request.POST.dict()
        else:
            params = request.GET.dict()
            
        return self.validator.validate(url, params, signature)

    async def process_message(self, request_data):
        """Process incoming WhatsApp message"""
        # Extract message details
        whatsapp_number = request_data.get('From', '').replace('whatsapp:', '')
        message_body = request_data.get('Body', '')
        media_url = request_data.get('MediaUrl0', None)
        message_sid = request_data.get('MessageSid', '')

        # Get or create chat session
        platform = await TwilioService.get_platform()
        chat_session = await ChatService.get_or_create_session(
            platform=platform,
            external_id=whatsapp_number
        )

        # Store the message
        platform = PlatformIntegration.objects.get(platform='whatsapp')
        message = PlatformMessage.objects.create(
            platform=platform,
            external_id=message_sid,
            chat_session=chat_session,
            direction='in',
            content=message_body,
            metadata={
                'media_url': media_url,
                'whatsapp_number': whatsapp_number
            }
        )

        # Process message through chatbot
        response = await ChatService.process_message(
            chat_session,
            message_body
        )
        
        return response

@csrf_exempt
@require_POST
async def twilio_webhook(request):
    """Handle incoming WhatsApp messages via Twilio"""
    try:
        # Extract message details from Twilio request
        whatsapp_number = request.POST.get('From', '').replace('whatsapp:', '')
        message_content = request.POST.get('Body', '')
        
        # Ensure WhatsApp platform integration exists
        platform = await TwilioService.get_platform()
        
        # Get or create chat session
        session = await ChatService.get_or_create_session(
            platform='whatsapp',  # Use string identifier instead of platform object
            external_id=whatsapp_number
        )
        
        # Process message through chatbot
        response = await ChatService.process_message(
            session=session,
            message_content=message_content
        )
        
        # Create Twilio response
        twiml = MessagingResponse()
        twiml.message(response)
        
        return HttpResponse(str(twiml), content_type='text/xml')
        
    except Exception as e:
        # Log error and return generic message
        print(f"Error processing webhook: {str(e)}")
        twiml = MessagingResponse()
        twiml.message("Sorry, we're having trouble processing your message. Please try again later.")
        return HttpResponse(str(twiml), content_type='text/xml') 