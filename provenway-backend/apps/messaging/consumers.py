"""
apps/messaging/consumers.py
────────────────────────────
WebSocket consumer for real-time chat.
Implement fully in Track B (Weeks 11–14 per Build Plan).
"""

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for a conversation room.

    Channel group: chat_{conversation_id}
    All participants in a conversation are added to this group on connect.
    """

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"chat_{self.conversation_id}"

        # TODO (Track B): verify the user is a participant in this conversation
        # before accepting the connection.

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """Receive message from WebSocket, broadcast to group."""
        # TODO (Track B): validate, save to DB, then broadcast.
        data = json.loads(text_data or "{}")
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "chat.message", "payload": data},
        )

    async def chat_message(self, event):
        """Receive broadcast from group, forward to WebSocket client."""
        await self.send(text_data=json.dumps(event["payload"]))
