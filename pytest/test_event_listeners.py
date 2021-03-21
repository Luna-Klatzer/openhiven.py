import openhivenpy

token_ = ""
client = openhivenpy.UserClient()


def test_start(token):
    global token_
    token_ = token


class TestListeners:
    def test_on_init(self):
        @client.event()
        async def on_init():
            print("\non_init was called!")
            await client.close()

        client.run(token_)

    def test_on_ready(self):
        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        client.run(token_)

    def test_on_message_create(self):
        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.parsers.dispatch('message_create', {})

        @client.event()
        async def on_message_create():
            print("Received message")
            await client.close()

        client.run(token_)
