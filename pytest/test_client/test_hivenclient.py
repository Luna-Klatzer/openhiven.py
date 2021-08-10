import asyncio
import json
import os

import pkg_resources

import openhivenpy

token_ = ""


def test_start(token):
    global token_
    TestHivenClient.token = token


class TestHivenClient:
    token = token_

    def test_init(self):
        client = openhivenpy.HivenClient()

        @client.event()
        async def on_init():
            assert client.token == self.token
            print("\non_init was called!")

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        client.run(self.token)

    def test_force(self):
        client = openhivenpy.HivenClient()

        @client.event()
        async def on_init():
            assert client.token == self.token
            print("\non_init was called!")

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close(force=True)

        client.run(self.token)

    def test_run_twice(self):
        client = openhivenpy.HivenClient()

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        client.run(self.token)
        client.run(self.token)

    def test_run_with_env_token(self):
        openhivenpy.env.load_env()
        client = openhivenpy.HivenClient()

        try:
            assert client.token is None
            client.run()
        except openhivenpy.InvalidTokenError:
            pass
        else:
            assert False

        client = openhivenpy.HivenClient(token=os.getenv('HIVEN_TOKEN'))
        try:
            assert client.token == os.getenv('HIVEN_TOKEN')
            client.run()
        except openhivenpy.InvalidTokenError:
            pass
        else:
            assert False

    def test_pre_configured_token(self):
        client = openhivenpy.HivenClient(token=self.token)

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        assert client.token == self.token
        client.run()

    def test_connect(self):
        client = openhivenpy.HivenClient()

        @client.event()
        async def on_init():
            assert client.token == self.token
            print("\non_init was called!")

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.close()

        asyncio.run(client.connect(self.token))

    def test_queuing(self):
        client = openhivenpy.HivenClient(queue_events=True)

        @client.event()
        async def on_init():
            assert client.token == self.token
            print("\non_init was called!")

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            await client.parsers.dispatch('message_create', {})

        @client.event()
        async def on_message_create():
            print("Received message")
            await client.close()

        client.run(self.token)

    def test_long_run(self):
        client = openhivenpy.HivenClient()

        @client.event()
        async def on_ready():
            print("\non_ready was called!")
            client.message_broker.get_buffer("message_create").add_new_event(
                {}, (), {})

        @client.event()
        async def on_message_create():
            await asyncio.sleep(10)
            await client.close()

        client.run(self.token)

    def _read_config_file(self):
        with open(pkg_resources.resource_filename(__name__, "test_data.json"), 'r') as file:
            return json.load(file)

    def test_find(self):
        client = openhivenpy.HivenClient()
        _data = self._read_config_file()
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
