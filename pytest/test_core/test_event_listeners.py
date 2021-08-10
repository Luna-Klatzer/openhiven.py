import pytest

import openhivenpy

token_ = ""


def test_start(token):
    global token_
    token_ = token


class TestListeners:
    def test_on_init(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_init():
            print("\non_init was called!")
            await _client.close()

        _client.run(token_)

    def test_on_ready(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.close()

        _client.run(token_)

    @pytest.mark.parametrize(
        "old,new", [
            (
                    {
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
                    },
                    {
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
            ),
            (
                    {
                        "bio": "example2",
                        "bot": True,
                        "email_verified": True,
                        "header": "",
                        "icon": "",
                        "id": "123456789123456789",
                        "location": "",
                        "name": "example",
                        "user_flags": 0,
                        "username": "Example"
                    },
                    {
                        "bio": "example3",
                        "bot": True,
                        "email_verified": True,
                        "header": "",
                        "icon": "",
                        "id": "123456789123456789",
                        "location": "",
                        "name": "example",
                        "user_flags": 0,
                        "username": "Example"
                    }
            )
        ]
    )
    def test_on_user_update(self, old: dict, new: dict):
        _client = openhivenpy.UserClient()

        _client.storage['users']['123456789123456789'] = dict(old)

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('user_update', new)

        @_client.event()
        async def on_user_update(old_user, new_user):
            print("\non_user_update was called!")
            assert old_user.bio == old['bio']
            assert new_user.bio == new['bio']
            assert old_user.bio != new_user.bio
            assert old_user.bot == new_user.bot
            assert old_user.id == new_user.id
            await _client.close()

        _client.run(token_)

    # Empty tests due to missing implementation

    def test_on_house_join(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('house_join', {})

        @_client.event()
        async def on_house_join(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_house_remove(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('house_remove', {})

        @_client.event()
        async def on_house_remove(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_house_update(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('house_update', {})

        @_client.event()
        async def on_house_update(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_house_delete(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('house_delete', {})

        @_client.event()
        async def on_house_delete(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_house_downtime(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('house_downtime', {})

        @_client.event()
        async def on_house_downtime(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_room_create(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('room_create', {})

        @_client.event()
        async def on_room_create(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_room_update(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('room_update', {})

        @_client.event()
        async def on_room_update(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_room_delete(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('room_delete', {})

        @_client.event()
        async def on_room_delete(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_house_member_join(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('house_member_join', {})

        @_client.event()
        async def on_house_member_join(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_house_member_leave(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('house_member_leave', {})

        @_client.event()
        async def on_house_member_leave(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_house_member_enter(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('house_member_enter', {})

        @_client.event()
        async def on_house_member_enter(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_house_member_update(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('house_member_update', {})

        @_client.event()
        async def on_house_member_update(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_house_member_exit(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('house_member_exit', {})

        @_client.event()
        async def on_house_member_exit(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_house_member_chunk(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('house_member_chunk', {})

        @_client.event()
        async def on_house_member_chunk(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_relationship_update(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('relationship_update', {})

        @_client.event()
        async def on_relationship_update(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_presence_update(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('presence_update', {})

        @_client.event()
        async def on_presence_update(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_message_create(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('message_create', {})

        @_client.event()
        async def on_message_create(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_message_update(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('message_update', {})

        @_client.event()
        async def on_message_update(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_message_delete(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('message_delete', {})

        @_client.event()
        async def on_message_delete(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)

    def test_on_typing_start(self):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch('typing_start', {})

        @_client.event()
        async def on_typing_start(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token_)
