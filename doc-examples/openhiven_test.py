"""
Test-file for testing purposes and development!
"""

import asyncio
import openhivenpy
from openhivenpy import utils
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='tests/openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = openhivenpy.UserClient(token="")


@client.event()
async def on_connection_start():
    print("Connection established")


@client.event()
async def on_init(time):
    print(f"Init'd at {time}")


@client.event() 
async def on_ready():
    print(f"Ready after {client.startup_time}")

    house = await client.get_house(175036727902074248)

    update_room = utils.get(house.rooms, name="Announcements")
    await update_room.edit(name="Updates")

    url = await client.fetch_invite("openhivenpy")

    house = await client.create_house("test house")

    await asyncio.sleep(1)
    house = openhivenpy.utils.get(client.houses, id=house.id)

    await house.create_room(name="stuff")
    
    room = house.rooms[0]
    
    await room.send("test")
    
    await house.delete()
    
    feed = await client.get_feed()
    
    mentions = await client.get_mentions()
    
    friend_request = await client.fetch_current_friend_requests()
    
    private_room = await client.get_private_room(175699760957616349)

    print(friend_request)

    # await client.create_private_room()


@client.event()
async def on_message_create(message):
    print(message.content)


@client.event()
async def on_house_join(house):
    print(house.name)


@client.event()
async def on_house_remove(house):
    print(house.name)


@client.event()
async def on_house_downage(t, house):
    print(f"{house.name} was reported to be done at {t}")


@client.event()
async def on_typing_start(typing):
    print(typing)


@client.event()
async def on_house_member_exit(user, house):
    print(f"{user.name} left {house.name}")


@client.event()
async def on_house_member_enter(member, house):
    print(f"{member.name} joined {house.name}")

if __name__ == '__main__':
    # Async Startup
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(client.connect())

    # Regular Startup
    client.run()
