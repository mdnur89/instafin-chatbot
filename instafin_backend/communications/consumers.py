import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatSession, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.session_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        
        # Verify user has access to this chat
        if not await self.can_access_chat():
            await self.close()
            return

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = data['message']
            
            # Save message to database
            saved_message = await self.save_message(message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'content': saved_message.content,
                        'sender_id': saved_message.sender.id,
                        'timestamp': saved_message.timestamp.isoformat(),
                        'attachment': saved_message.attachment.url if saved_message.attachment else None
                    }
                }
            )
        elif message_type == 'typing':
            # Broadcast typing status
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'user_id': self.scope['user'].id
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def user_typing(self, event):
        # Send typing status to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id']
        }))

    @database_sync_to_async
    def can_access_chat(self):
        try:
            session = ChatSession.objects.get(id=self.session_id)
            user = self.scope['user']
            return user == session.user or user == session.agent
        except ChatSession.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message_data):
        session = ChatSession.objects.get(id=self.session_id)
        return ChatMessage.objects.create(
            session=session,
            sender=self.scope['user'],
            content=message_data['content'],
            attachment=message_data.get('attachment')
        ) 