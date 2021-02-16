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
