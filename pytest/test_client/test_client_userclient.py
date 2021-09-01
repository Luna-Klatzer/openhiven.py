import openhivenpy
import test_hivenclient


class TestUserClient(test_hivenclient.TestHivenClient):
    def test_init(self, token):
        client = openhivenpy.UserClient()
        assert client.client_type == 'UserClient'
        assert client.heartbeat == 30000
        assert client.close_timeout == 60

        @client.event()
        async def on_init():
            assert client.token == token
            print("\non_init was called!")

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        client.run(token)
