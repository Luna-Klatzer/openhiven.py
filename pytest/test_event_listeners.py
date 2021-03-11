import random
import openhivenpy
import asyncio

token_ = ""


def test_start(token):
    global token_
    token_ = token


class TestBotClient:
    def test_on_message_create(self):
        client = openhivenpy.HivenClient(token_)

        @client.event()
        async def on_init():
            print("\non_init was called!")

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.parsers.dispatch('message_create', {})

        @client.event()
        async def on_message_create():
            print("Received message")
            await client.close()

        client.run()
