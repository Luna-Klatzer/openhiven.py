import asyncio
import json
import os
from pathlib import Path

import openhivenpy


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


class TestHivenClient:
    def test_init(self, token):
        client = openhivenpy.HivenClient()

        @client.event()
        async def on_init():
            assert client.token == token
            print("\non_init was called!")

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        client.run(token)

    def test_force(self, token):
        client = openhivenpy.HivenClient()

        @client.event()
        async def on_init():
            assert client.token == token
            print("\non_init was called!")

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close(force=True)

        client.run(token)

    def test_run_twice(self, token):
        client = openhivenpy.HivenClient()

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close(remove_listeners=False)

        client.run(token)
        client.run(token)

    def test_run_with_env_token(self):
        openhivenpy.env.load_env()
        client = openhivenpy.HivenClient()

        try:
            assert client.token is None
            client.run()
        except openhivenpy.InvalidTokenError:
            pass
        else:
            openhivenpy.env.load_env(search_other=False)
            assert False

        client = openhivenpy.HivenClient(token=os.getenv('HIVEN_TOKEN'))
        try:
            assert client.token == os.getenv('HIVEN_TOKEN')
            client.run()
        except openhivenpy.InvalidTokenError:
            pass
        else:
            openhivenpy.env.load_env(search_other=False)
            assert False

        # Resetting to default
        openhivenpy.env.load_env(search_other=False)

    def test_pre_configured_token(self, token):
        client = openhivenpy.HivenClient(token=token)

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        assert client.token == token
        client.run()

    def test_connect(self, token):
        client = openhivenpy.HivenClient()

        @client.event()
        async def on_init():
            assert client.token == token
            print("\non_init was called!")

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        asyncio.run(client.connect(token))

    def test_queuing(self, token):
        client = openhivenpy.HivenClient(queue_events=True)

        @client.event()
        async def on_init():
            assert client.token == token
            print("\non_init was called!")

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            user = list(client.storage['users'].values())[0]
            await client.parsers.dispatch(
                'presence_update', user
            )

        @client.event()
        async def on_presence_update(user):
            assert user
            print("Received")
            await client.close()

        client.run(token)

    def test_long_run(self, token):
        client = openhivenpy.HivenClient()

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            user = list(client.storage['users'].values())[0]
            await client.parsers.dispatch(
                'presence_update', user
            )

        @client.event()
        async def on_presence_update(user):
            assert user
            print("Received")
            await asyncio.sleep(10)
            await client.close()

        client.run(token)

    def test_find(self):
        client = openhivenpy.HivenClient()
        _data = read_config_file()
        house_data = _data['house_data']
        relationship_data = _data['relationship_data']
        private_room_data = _data['private_room_data']
        private_group_room_data = _data['private_group_room_data']

        client.storage.update_client_user(house_data['members'][0]['user'])

        result_house_data = client.storage.add_or_update_house(house_data)
        result_relationship_data = client.storage.add_or_update_relationship(relationship_data)
        room_data = openhivenpy.TextRoom.format_obj_data(house_data['rooms'][0])
        user_data = openhivenpy.User.format_obj_data(house_data['members'][0]['user'])

        house_data['entities'][0]['house_id'] = house_data['id']
        entity_data = openhivenpy.Entity.format_obj_data(house_data['entities'][0])

        result_private_room_data = client.storage.add_or_update_private_room(private_room_data)
        result_private_group_room_data = client.storage.add_or_update_private_room(private_group_room_data)

        openhivenpy.PrivateRoom.format_obj_data(private_room_data)
        openhivenpy.PrivateGroupRoom.format_obj_data(private_group_room_data)

        assert result_house_data == client.find_house(house_data['id'])
        assert room_data == client.find_room(house_data['rooms'][0]['id'])
        assert user_data == client.find_user(house_data['members'][0]['user_id'])
        assert result_relationship_data == client.find_relationship(relationship_data['user_id'])
        assert entity_data == client.find_entity(entity_data['id'])
        assert result_private_room_data == client.find_private_room(private_room_data['id'])
        assert result_private_group_room_data == client.find_private_group_room(private_group_room_data['id'])
