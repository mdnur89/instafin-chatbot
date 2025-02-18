from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from instafin_backend.settings import PAGE_ACCESS_TOKEN ,VERIFY_TOKEN
import json
import requests
from .services import handle_user_interaction


VERIFY_TOKEN = VERIFY_TOKEN
PAGE_ACCESS_TOKEN = PAGE_ACCESS_TOKEN


@csrf_exempt
def messenger_webhook(request):
    if request.method == 'GET':
        # Handle Facebook Webhook Verification
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse("Forbidden", status=403)

    elif request.method == 'POST':
        # Handle Incoming Messages
        body = json.loads(request.body.decode('utf-8'))

        if body.get('object') == 'page':
            for entry in body.get('entry', []):
                for event in entry.get('messaging', []):
                    sender_id = event['sender']['id']
                    if 'message' in event and 'text' in event['message']:
                        message_text = event['message']['text']

                        # Handle user interaction based on the message text
                        response = handle_user_interaction(sender_id, message_text)
                        
                        # Send the response back to the user
                        send_message(sender_id, response['message'])
                        
                        # If there's a menu, send it as well
                        if 'menu' in response:
                            send_message(sender_id, "\n".join(response['menu']))
                    
                    else:
                        # Handle cases where the message does not contain text
                        send_message(sender_id, "Please send a text message.")

            return HttpResponse("EVENT_RECEIVED", status=200)

        else:
            return HttpResponse("Forbidden", status=403)

    return HttpResponse("Method Not Allowed", status=405)

def send_message(recipient_id, message_text):
    """
    Send a message to the specified recipient.
    """
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    response = requests.post("https://graph.facebook.com/v12.0/me/messages", params=params, headers=headers, data=data)
    return response.json()