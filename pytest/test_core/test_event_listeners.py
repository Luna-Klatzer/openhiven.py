import asyncio
import datetime
import json
import os
from copy import deepcopy
from pathlib import Path

import pytest

import openhivenpy
from openhivenpy import House, Message, User, TextRoom

OPENHIVENPY_TEST_HOUSE_ID = "276672055112364464"
OPENHIVENPY_TEST_ROOM_ID = "285087212549176390"


def read_config_file():
    """
    Reads the data from the config file - duplicate to avoid import troubles
    """
    path = Path("../test_data.json").resolve()
    if not os.path.exists(path):
        path = Path("./test_data.json").resolve()
        if not os.path.exists(path):
            raise RuntimeError("Cannot locate test_data.json")

    with open(path, 'r') as file:
        return json.load(file)


class TestListeners:

    def test_on_init(self, token):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_init():
            print("\non_init was called!")
            await _client.close()

        _client.run(token)

    def test_on_ready(self, token):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.close()

        _client.run(token)

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
                        "flags": 0,
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
                        "flags": 0,
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
                        "flags": 0,
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
                        "flags": 0,
                        "username": "Example"
                    }
            )
        ]
    )
    def test_on_user_update(self, old: dict, new: dict, token):
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

        _client.run(token)

    # Empty tests due to missing implementation

    def test_on_house_join(self, token):
        data = read_config_file().get("house_data")
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")
            await _client.parsers.dispatch(
                'house_join', data
            )

        @_client.event()
        async def on_house_join(house):
            assert type(house) is House
            assert house.name == data.get("name")
            assert house.id == data.get("id")
            await _client.close()

        _client.run(token)

    def test_on_house_down_and_delete(self, token):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")

            _ = _client.storage['houses']
            _id = _.get(list(_.keys())[0])["id"]

            await _client.parsers.dispatch(
                'house_down', {
                    "unavailable": True,
                    "house_id": _id
                }
            )

            await _client.parsers.dispatch(
                'house_down', {
                    "unavailable": False,
                    "house_id": _id
                }
            )

        @_client.event()
        async def on_house_down(house_id):
            assert house_id

        @_client.event()
        async def on_house_delete(house_id):
            assert house_id
            assert house_id not in _client.house_ids
            await _client.close()

        _client.run(token)

    def test_on_house_update(self, token):
        data = read_config_file().get("house_data")
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")

            await _client.parsers.dispatch(
                'house_join', data
            )

            while data['id'] not in _client.house_ids:
                await asyncio.sleep(0.05)

            new_data: dict = deepcopy(data)
            new_data.update({"name": "test"})  # changing the name
            await _client.parsers.dispatch('house_update', new_data)

        @_client.event()
        async def on_house_update(old, new):
            assert old.id == new.id
            assert new.name == "test"
            assert data["name"] != "test"
            await _client.close()

        _client.run(token)

    def test_on_house_leave(self, token):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")

            _ = _client.storage['houses']
            first_item_id = list(_.keys())[0]
            await _client.parsers.dispatch(
                'house_leave', {
                    "id": _client.id,
                    "house_id": first_item_id
                }
            )

        @_client.event()
        async def on_house_leave(house_id):
            assert house_id
            assert house_id not in _client.house_ids
            await _client.close()

        _client.run(token)

    def test_on_presence_update(self, token):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")

            user = list(_client.storage['users'].values())[0]
            await _client.parsers.dispatch(
                'presence_update', user
            )

        @_client.event()
        async def on_presence_update(*args, **kwargs):
            print("Received")
            await _client.close()

        _client.run(token)

    def test_on_message_create(self, token):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")

            # TODO! Change with Mock API
            house = _client.get_house(OPENHIVENPY_TEST_HOUSE_ID)
            room = house.get_room(OPENHIVENPY_TEST_ROOM_ID)
            await room.send("Test message from openhiven.py")

        @_client.event()
        async def on_message_create(msg: Message):
            await msg.delete()
            print("Received")
            await _client.close()

        _client.run(token)

    def test_on_message_update(self, token):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")

            house = _client.get_house(OPENHIVENPY_TEST_HOUSE_ID)
            room = house.get_room(OPENHIVENPY_TEST_ROOM_ID)
            msg = await room.send("Test message from openhiven.py")
            await msg.edit("Test message from openhiven.py (edited)")

        @_client.event()
        async def on_message_update(msg: Message):
            assert msg
            print("Received")
            await _client.close()

        _client.run(token)

    def test_on_message_delete(self, token):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")

            # TODO! Change with Mock API
            house = _client.get_house(OPENHIVENPY_TEST_HOUSE_ID)
            room = house.get_room(OPENHIVENPY_TEST_ROOM_ID)
            await room.send("Test message from openhiven.py")

        @_client.event()
        async def on_message_create(msg: Message):
            await msg.delete()

        @_client.event()
        async def on_message_delete(msg_id: str, room_id: str, house_id: str):
            assert msg_id
            assert room_id in _client.room_ids
            assert house_id in _client.house_ids

            print("Received")
            await _client.close()

        _client.run(token)

    def test_on_typing_start(self, token):
        _client = openhivenpy.UserClient()

        @_client.event()
        async def on_ready():
            print("\non_ready was called!")

            room = _client.get_room(OPENHIVENPY_TEST_ROOM_ID)
            await room.start_typing()

        @_client.event()
        async def on_typing_start(
                user: User, room: TextRoom, timestamp: datetime.datetime
        ):
            assert user
            assert room
            assert timestamp

            print("Received")
            await _client.close()

        _client.run(token)
