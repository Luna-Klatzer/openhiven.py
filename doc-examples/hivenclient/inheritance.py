import logging

import openhivenpy as hiven

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Bot(hiven.UserClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f"Bot is ready after {self.startup_time}s")

    async def on_user_update(self, old, new):
        print(f"{old.name} updated their account")

    async def on_message_create(self, msg):
        print(f"{msg.author.name} wrote in {msg.room.name}: {msg.content}")

    async def on_house_member_join(self, member, house):
        print(f"{member.name} joined {house.name}")

    async def on_typing_start(self, typing):
        print(f"{author.name} started typing ...")

    async def on_member_update(self, old, new, house):
        print(f"Member {old.name} of house {house.name} updated their account")

    async def on_message_update(self, msg):
        print(f"{msg.author.name} updated their message to: {msg.content}")

    async def on_room_create(self, room):
        print(f"{repr(room)} was created")


if __name__ == '__main__':
    client = Bot()
    client.run("Insert token", restart=True)
