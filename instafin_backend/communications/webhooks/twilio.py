from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from django.conf import settings
from ..models import PlatformMessage, PlatformIntegration
from ..services.chat_service import ChatService

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
        chat_session = await ChatService.get_or_create_session(
            platform='whatsapp',
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
    handler = TwilioWebhookHandler()
    
    # Validate request is from Twilio
    if not handler.validate_request(request):
        return HttpResponse(status=403)
    
    try:
        # Process the message
        response = await handler.process_message(request.POST)
        
        # Create TwiML response
        twiml = MessagingResponse()
        if response:
            twiml.message(response)
        
        return HttpResponse(str(twiml), content_type='text/xml')
        
    except Exception as e:
        # Log the error and return empty 200 response to acknowledge receipt
        logger.error(f"Error processing Twilio webhook: {str(e)}")
        return HttpResponse(status=200) 