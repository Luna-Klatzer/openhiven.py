""" Test-file for testing purposes and development! """
import logging

import openhivenpy

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = openhivenpy.UserClient()


@client.event() 
async def on_ready():
    print(f"Ready after {client.startup_time}")


@client.event()
async def on_message_create():
    print(f"Message was created")


if __name__ == '__main__':
    client.run("y9JvliBe8fbOmmSAmS09sHvWk6FVV2ZdOtVenZAsoN0xH3OwXmJZIooTh3PuKyECp0UUDDfuS6gT6MbaBDYecryEky4HS2LMq1Sp3WM5u7jakITMON5QXk9NseiL3Syr", )
