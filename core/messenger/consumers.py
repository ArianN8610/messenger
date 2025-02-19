import re
import json
import html

import bleach
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from accounts.models import User
from .models import Message, PrivateChat


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Create WebSocket connection and add user to the chat group"""
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_name = f"private_chat_{self.chat_id}"

        # Add connection to WebSocket group
        await self.channel_layer.group_add(self.chat_name, self.channel_name)  # Add current user to the chat group. This will cause messages from this group to be sent to them.
        await self.accept()  # It verifies the WebSocket connection and the connection is established

    async def disconnect(self, close_code):
        """Remove user from chat group when disconnected"""
        await self.channel_layer.group_discard(self.chat_name, self.channel_name)

    async def receive(self, text_data):
        """Receive message, save it in the DB, and send it to the group"""
        data = json.loads(text_data)
        message = data['message']
        sender_id = data['sender_id']

        # Convert HTML entities like &nbsp; to real spaces
        message = html.unescape(message)
        # Remove extra `<br>` from the beginning and end
        message = re.sub(r'^(<br>\s*)+|(<br>\s*)+$', '', message, flags=re.IGNORECASE).strip()
        # If the message is empty after removing the spaces, don't send it!
        if not message:
            return
        message = bleach.clean(message, tags=['br'], strip=True)

        chat = await sync_to_async(PrivateChat.objects.get)(id=self.chat_id)
        sender = await sync_to_async(User.objects.get)(id=sender_id)

        # Save message in database
        new_message = await sync_to_async(Message.objects.create)(
            chat=chat, sender=sender, content=message
        )

        # Send new message to the WebSocket group
        await self.channel_layer.group_send(
            self.chat_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'sent_at': new_message.sent_at.strftime('%H:%M'),
            }
        )

    async def chat_message(self, event):
        """Send message to all connected users"""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sent_at': event['sent_at'],
        }))
