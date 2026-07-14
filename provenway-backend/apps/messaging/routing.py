"""apps/messaging/routing.py — WebSocket routes for chat."""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # wss://api.provenway.co.ke/ws/chat/{conversation_id}/
    re_path(r"ws/chat/(?P<conversation_id>[0-9a-f-]+)/$", consumers.ChatConsumer.as_asgi()),
]
