import json
import html

import bleach
from django.db.models import Q
from bleach.linkifier import Linker
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from accounts.models import User
from .models import Message, PrivateChat


def add_custom_attrs(tag, name, value):
    """Add custom attributes to <a> tags in bleach"""
    if name == 'href':
        return value  # Keep the href attribute
    elif name == 'target':
        return '_blank'  # Open links in a new tab
    elif name == 'rel':
        return 'noopener noreferrer'  # Security best practice

    return None  # Remove all other attributes


def set_class(attrs, new=False):
    """Set class attribute for <a> tags"""
    attrs[(None, 'class')] = 'link link-primary'
    return attrs


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
        message = html.unescape(message).strip()

        # Clean content with bleach
        message = bleach.clean(
            message,
            tags=['br', 'p', 'a', 'i', 'strong', 'u', 's', 'sub', 'sup'],
            attributes={'a': add_custom_attrs},
            strip=True
        )

        # Convert plain URLs to clickable links and add attributes
        linker = Linker(callbacks=[set_class])
        message = linker.linkify(message)

        # If the message is empty after removing the spaces, don't send it!
        if not message:
            return

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

        # Send message to update the sender and recipient chats
        await self.channel_layer.group_send(
            f"user_{sender.id}_chats",
            {"type": "update_chat_list"}
        )

        other_user = await sync_to_async(chat.get_other_user)(sender)
        await self.channel_layer.group_send(
            f"user_{other_user.id}_chats",
            {"type": "update_chat_list"}
        )

    async def chat_message(self, event):
        """Send message to all connected users"""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sent_at': event['sent_at'],
        }))


class ChatListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """When the user connects, add them to a specific group"""
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
        else:
            self.group_name = f"user_{self.user.id}_chats"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        """When the user leaves, remove them from the group"""
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def update_chat_list(self, event):
        """Sending useless value just to activate websocket"""
        await self.send(text_data=json.dumps({'status': 'ping'}))
