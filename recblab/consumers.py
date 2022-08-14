import asyncio

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from recblab.models import Room


class RoomConsumer(AsyncJsonWebsocketConsumer):
    def get_room(self, room_id):
        room, created = Room.objects.get_or_create(id=room_id)
        return room

    def add_user_to_room(self, user, room):
        was_added = False
        if user not in room.members.all():
            room.members.add(user)
            was_added = True
        members = [user["display_name"] for user in room.members.all().values()]
        return members, was_added

    def set_room_privacy(self, private):
        self.room.private = private
        self.room.save()

    async def connect(self):
        await self.accept()

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room = await database_sync_to_async(self.get_room)(self.room_id)
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.room_id, self.channel_name)
        members, was_added = await database_sync_to_async(self.add_user_to_room)(
            self.user, self.room
        )
        if was_added:
            await self.channel_layer.group_send(
                self.room_id,
                {"type": "members", "members": members},
            )
        else:
            await self.channel_layer.send(
                self.channel_name, {"type": "members", "members": members}
            )
        await self.channel_layer.send(
            self.channel_name, {"type": "privacy", "privacy": self.room.private}
        )

        await self.channel_layer.group_send(
            self.user.username,
            {
                "type": "hello",
                "hello": "world",
            },
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(str(self.room.id), self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("command") == "update_privacy":
            asyncio.create_task(self.update_privacy(content))

    async def update_privacy(self, input_payload):
        await database_sync_to_async(self.set_room_privacy)(input_payload["privacy"])
        await self.channel_layer.group_send(
            self.room_id,
            {"type": "privacy", "privacy": self.room.private},
        )

    async def members(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def privacy(self, event):
        # Send message to WebSocket
        await self.send_json(event)


class UserConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.username = str(self.scope["url_route"]["kwargs"]["user_id"])
        user = self.scope["user"]
        if self.username == user.username:
            await self.channel_layer.group_add(self.username, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.username, self.channel_name)

    async def hello(self, event):
        # Send message to WebSocket
        await self.send_json(event)
