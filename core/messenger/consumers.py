import json
import html
from datetime import datetime

import bleach
from bleach.linkifier import Linker
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from accounts.models import User, Profile
from .models import Message, PrivateChat
from .templatetags.messenger_tags import last_seen_display


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
        """Receive message"""
        data = json.loads(text_data)
        message_type = data.get('type', 'message')  # Default is 'message'

        match message_type:
            case 'message':
                await self.handle_message(data)
            case 'seen':
                await self.handle_seen(data)
            case 'delete':
                await self.handle_delete_message(data)

    async def handle_message(self, data):
        """Save message in the DB, and send it to the group"""
        message = data['message']
        sender_id = data['sender_id']
        reply_id = data['reply']

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
        if reply_id:
            reply_message = await sync_to_async(Message.objects.get)(id=reply_id)
        else:
            reply_message = None

        # Save message in database
        new_message = await sync_to_async(Message.objects.create)(
            chat=chat, sender=sender, content=message, reply_to=reply_message
        )

        # Send new message to the WebSocket group
        await self.channel_layer.group_send(
            self.chat_name,
            {
                "type": "broadcast",
                "action": "message",
            }
        )

        await self.update_chat_list()

    async def handle_seen(self, data):
        """Mark messages as read"""
        message_id = data['message_id']
        user_id = data['user_id']

        message = await sync_to_async(Message.objects.get)(id=message_id)
        user = await sync_to_async(User.objects.get)(id=user_id)

        await sync_to_async(message.mark_as_read)(user)

        await self.channel_layer.group_send(
            self.chat_name,
            {
                "type": "broadcast",
                "action": "seen",
                "user_id": user_id
            }
        )
        await self.update_chat_list()

    async def handle_delete_message(self, data):
        """Delete specified message"""
        message_id = data['message_id']
        user_id = data['user_id']

        message = await sync_to_async(Message.objects.select_related('sender', 'chat').get)(id=message_id)

        if message.sender.id == user_id and message.chat.id == int(self.chat_id):
            await sync_to_async(message.delete)()

        await self.channel_layer.group_send(
            self.chat_name,
            {
                "type": "broadcast",
                "action": "delete",
            }
        )
        await self.update_chat_list()

    async def update_chat_list(self):
        """Send message to update the sender and recipient chats"""
        chat = await sync_to_async(PrivateChat.objects.get)(id=self.chat_id)
        user1_id = await sync_to_async(lambda: chat.user1.id)()
        user2_id = await sync_to_async(lambda: chat.user2.id)()

        await self.channel_layer.group_send(
            f"user_{user1_id}_chats",
            {"type": "update_chat_list"}
        )

        await self.channel_layer.group_send(
            f"user_{user2_id}_chats",
            {"type": "update_chat_list"}
        )

    async def broadcast(self, event):
        """Send a broadcast message to web socket group"""
        await self.send(text_data=json.dumps(event))


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


class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = 'users_status'

        await self.update_user_status(True)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.update_user_status(False, datetime.now())
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Receive message"""
        data = json.loads(text_data)
        message_type = data.get('type', 'online')

        if message_type == 'online':
            await self.update_user_status(True)
        elif message_type == 'offline':
            await self.update_user_status(False, datetime.now())

    async def update_user_status(self, is_online, last_seen=None):
        """Update user status in the DB"""

        # Get user from DB
        user = await sync_to_async(Profile.objects.get)(user=self.user)

        # Update user data in the DB
        user.is_online = is_online
        if last_seen:
            user.last_seen = last_seen

        # Save user
        await sync_to_async(user.save)()

        # Send a message to all users in the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'broadcast',
                'is_online': is_online,
                'user_id': self.user.id,
                'last_seen': last_seen_display(last_seen) if last_seen is not None else '',
            }
        )

    async def broadcast(self, event):
        await self.send(text_data=json.dumps(event))
