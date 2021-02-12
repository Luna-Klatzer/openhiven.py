import asyncio

import openhivenpy as hiven
import logging

from openhivenpy.utils import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Bot(hiven.UserClient):
    def __init__(self, token, *args, **kwargs):
        self._token = token
        super().__init__(token, *args, **kwargs)

    # Not directly needed but protects the token from ever being changed!
    @property
    def token(self):
        return self._token

    async def on_ready(self):
        print(f"Bot is ready after {self.startup_time}s")
        invite = await self.fetch_invite("openhivenpy")
        print(invite)
        print(await self.fetch_current_friend_requests())

        robyn_channel = self.fetch_private_room(175699760957616349)
        print(robyn_channel.name)

        house = await self.create_house("A pretty good House")
        await asyncio.sleep(.5)
        house = self.fetch_house(house.id)

        room = house.get_room(house.rooms[0].id)
        msg = await room.send("test")
        await msg.edit("g")
        await msg.delete()

        entity = await house.create_entity("stuff")
        print(entity.name)

        invite = await house.create_invite(24)
        print(invite)

        await house.edit(name="d")
        await asyncio.sleep(.5)
        house = self.fetch_house(house.id)
        print(house.name)

        await house.delete()

    async def on_user_update(self, old, new):
        print(f"{old.name} updated their account")

    async def on_message_create(self, msg):
        print(f"{msg.author.name} wrote in {msg.room.name}: {msg.content}")

    async def on_house_member_join(self, member, house):
        print(f"{member.name} joined {house.name}")

    async def on_typing_start(self, typing):
        print(f"{typing.author.name} started typing ...")

    async def on_member_update(self, old, new, house):
        print(f"Member {old.name} of house {house.name} updated their account")

    async def on_message_update(self, msg):
        print(f"{msg.author.name} updated their message to: {msg.content}")

    async def on_room_create(self, room):
        print(f"{repr(room)} was created")


if __name__ == '__main__':
    client = Bot("")
    client.run(restart=True)
