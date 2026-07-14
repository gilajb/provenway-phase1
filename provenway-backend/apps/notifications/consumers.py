"""
apps/notifications/consumers.py
────────────────────────────────
WebSocket consumer for real-time notifications.
Implement fully in Track A (Weeks 9–11 per Build Plan).
"""

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for per-user notification push.

    Channel group: notifications_{user_id}
    Only the authenticated user is added to their own group.
    """

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return

        self.user_id = str(user.id)
        self.group_name = f"notifications_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """Clients don't send on this socket — read-only push channel."""
        pass

    async def notification_push(self, event):
        """Receive broadcast from Celery task, forward to WebSocket client."""
        await self.send(text_data=json.dumps(event["payload"]))
