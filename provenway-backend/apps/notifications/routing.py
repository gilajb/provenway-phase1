"""apps/notifications/routing.py — WebSocket routes for notifications."""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # wss://api.provenway.co.ke/ws/notifications/
    re_path(r"ws/notifications/$", consumers.NotificationConsumer.as_asgi()),
]
