import openhivenpy
import test_hivenclient


class TestBotClient(test_hivenclient.TestHivenClient):
    def test_init(self, token):
        client = openhivenpy.BotClient()
        assert client.client_type == 'BotClient'
        assert client.connection.heartbeat == 30000
        assert client.connection.close_timeout == 60

        @client.event()
        async def on_init():
            assert client.token == token
            print("\non_init was called!")

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        client.run(token)
