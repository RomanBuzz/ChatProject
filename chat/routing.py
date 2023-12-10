# chat/routing.py

from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    path("ws/room-list/", consumers.RoomListConsumer.as_asgi()),
]
