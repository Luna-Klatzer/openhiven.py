import openhivenpy

token_ = ""


def test_start(token):
    global token_
    token_ = token


class TestListeners:
    def test_on_init(self):
        client = openhivenpy.UserClient()
        @client.event()
        async def on_init():
            print("\non_init was called!")
            await client.close()

        client.run(token_)

    def test_on_ready(self):
        client = openhivenpy.UserClient()
        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        client.run(token_)

    def test_on_user_update(self):
        client = openhivenpy.UserClient()
        old = {
            "bio": "example",
            "bot": False,
            "email_verified": False,
            "header": "",
            "icon": "",
            "id": "123456789123456789",
            "location": "",
            "name": "example",
            "user_flags": 0,
            "username": "Example"
        }

        client.storage['users']['123456789123456789'] = dict(old)

        new = {
            "bio": "example2",
            "bot": False,
            "email_verified": False,
            "header": "",
            "icon": "",
            "id": "123456789123456789",
            "location": "",
            "name": "example",
            "user_flags": 0,
            "username": "Example"
        }

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.parsers.dispatch('user_update', new)

        @client.event()
        async def on_user_update(old_user, new_user):
            print("\non_user_update was called!")
            assert old_user.bio == old['bio']
            assert new_user.bio == new['bio']
            assert old_user.bio != new_user.bio
            await client.close()

        client.run(token_)

    def test_on_message_create(self):
        client = openhivenpy.UserClient()
        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.parsers.dispatch('message_create', {})

        @client.event()
        async def on_message_create(*args, **kwargs):
            print("Received message")
            await client.close()

        client.run(token_)
