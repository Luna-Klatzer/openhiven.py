"""
Test-file for testing purposes and development!
"""
import asyncio
import time
import openhivenpy
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
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

    url = await client.fetch_invite("openhivenpy")

    house = await client.create_house(name="test 2d")

    await asyncio.sleep(.1)

    house = openhivenpy.utils.get(client.houses, id=house.id)

    await house.create_room(name="stuff")
    
    room = house.rooms[0]
    
    print(await room.send("test"))
    
    print(await house.delete())
    
    feed = await client.get_feed()
    
    mentions = await client.get_mentions()
    
    friend_request = await client.fetch_current_friend_requests()
    
    private_room = await client.get_private_room(175699760957616349)

    print(friend_request)


@client.event()
async def on_message_create(message):
    print(f"{message.author.name} sent a message in {message.room.name}: {message.content}")


@client.event()
async def on_house_join(house):
    print(f"Joined {house.name}")


@client.event()
async def on_house_remove(house):
    print(f"Left {house.name}")


@client.event()
async def on_house_delete(house_id):
    print(f"{house_id} was deleted at {time.time()}")


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
