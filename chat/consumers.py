import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from datetime import datetime
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .models import Room, Message


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = Room.objects.get(name=self.room_name)
        self.user = self.scope['user']

        # connection has to be accepted
        self.accept()

        # creates chat message history for connected user from DB
        msg = Message.objects.filter(room=self.room).order_by('timestamp')
        chat_history = ""
        for i in msg:
            chat_history += f'{i}\n'

        # ads connected user to DB-room and creates current room users list from DB
        self.room.join(self.user)
        user_list = list(self.room.online.all().values_list("id", 'username'))

        # sends chat message history only to connected user
        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': chat_history,
        }))

        # Create or join to group(room) and assign channel_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # sends current room users list to all users when user connected
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'connection_status',
                'date': f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}]',
                'user_list': user_list,
                'user': self.user.username,
                'action': 'connected',
            }
        )

    def disconnect(self, close_code):

        # deletes disconnected user from DB-room and creates current room users list from DB
        self.room.leave(self.user)
        user_list = list(self.room.online.all().values_list("id", 'username'))

        # sends current room users list to all users when user disconnected
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'connection_status',
                'date': f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}]',
                'user_list': user_list,
                'user': self.user.username,
                'action': 'disconnected',
            }
        )

        # deletes disconnected user from a Django Channels group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        direction = text_data_json['direction']

        if not self.user.is_authenticated:
            return

        # sends received message to the room
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'date': f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}]',
                'user': self.user.username,
                'message': message,
                'direction': direction,
            }
        )

        # saves received public message in DB (private messages are not saved in DB)
        if direction == 'room':
            Message.objects.create(user=self.user, room=self.room, content=message)
            print(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}]', self.user, self.room, message)

    # Handler for "chat_message" type messages
    def chat_message(self, event):
        direction = event['direction']
        print(self.scope['user'].pk, direction, str(self.scope['user'].pk) == str(direction))
        # sends public message to all users
        if direction == 'room':
            self.send(text_data=json.dumps(event))
            print(json.dumps(event))
            print(self.scope['url_route']['kwargs'])
            print(self.scope['user'])
            print(self.room_name)
            print(self.room_group_name)
            print(self.channel_name)
        # sends private message to selected user
        elif str(self.scope['user'].pk) == str(direction):
            self.send(text_data=json.dumps(event))
            print(json.dumps(event))
            print(self.scope['url_route']['kwargs'])
            print(self.scope['user'])
            print(self.room_name)
            print(self.room_group_name)
            print(self.channel_name)

    # Handler for "connection_status" type messages
    # sends current room users list to all users when user connected or disconnected
    def connection_status(self, event):
        self.send(text_data=json.dumps(event))
        print(json.dumps(event))
        print(self.scope['url_route']['kwargs'])
        print(self.room_name)
        print(self.room_group_name)
        print(self.channel_name)


class RoomListConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        self.user = None

    def connect(self):
        self.room_group_name = 'room-list'
        self.user = self.scope['user']

        # connection has to be accepted
        self.accept()

        # creates current rooms list from DB
        rooms = [room.get_online_count for room in Room.objects.all()]

        # sends current rooms list to connected user
        self.send(text_data=json.dumps({
            'type': 'first_connect',
            'user': self.user.username,
            'action': 'first_connect',
            'message': rooms,
        }))

        # Create or join to group(room) and assign channel_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # sends console.log to all users when user connected
        # for further development - isn't necessary now
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'connection_status',
                'user': self.user.username,
                'action': 'connected',
            }
        )

    def disconnect(self, close_code):

        # sends console.log to all users when user disconnected
        # for further development - isn't necessary now
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'connection_status',
                'user': self.user.username,
                'action': 'disconnected',
            }
        )

        # deletes disconnected user from a Django Channels group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        room_name = text_data_json['room']
        description = text_data_json['description']

        if not self.user.is_authenticated:
            return

        # on 'room-delete': deletes the room in DB, creates new rooms list from DB and sends to all users
        if description == 'room-delete':
            room = Room.objects.get(name=room_name)
            if room.online.count() == 0:
                room.delete()
                rooms = [room.get_online_count for room in Room.objects.all()]
                message = {
                    'type': 'connection_status',
                    'action': 'refresh_rooms',
                    'message': rooms,
                }
                room_group_name = 'room-list'
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    room_group_name, message
                )
        # on 'room-rename': renames the room in DB
        elif description == 'room-rename':
            rename = text_data_json['rename']
            if not Room.objects.filter(name=rename).exists():
                room = Room.objects.get(name=room_name)
                if room.online.count() == 0:
                    room.name = rename
                    room.save()

    # on 'room-change' in DB: creates new rooms list from DB and sends to all users
    # doesn't work properly with post_delete signal - figure it out later
    @receiver([post_save, m2m_changed], sender=Room)
    def room_list(sender, instance, created, **kwargs):
        rooms = [room.get_online_count for room in Room.objects.all()]
        message = {
            'type': 'connection_status',
            'action': 'refresh_rooms',
            'message': rooms,
        }
        room_group_name = 'room-list'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
                    room_group_name, message
                )

    # Handler for "connection_status" type messages
    # sends for "connection_status" type messages to all users
    def connection_status(self, event):
        self.send(text_data=json.dumps(event))
        print(json.dumps(event))
        print(self.room_group_name)
        print(self.channel_name)
