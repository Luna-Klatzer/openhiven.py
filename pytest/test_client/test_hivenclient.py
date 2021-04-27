import asyncio

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
            client.message_broker.get_buffer("message_create").add({}, (), {})

        @client.event()
        async def on_message_create():
            await asyncio.sleep(10)
            await client.close()

        client.run(self.token)

    def test_find(self):
        house_data = {
            "rooms": [{
                "type": 0,
                "recipients": None,
                "position": 2,
                "permission_overrides": None,
                "owner_id": None,
                "name": "room",
                "last_message_id": None,
                "id": "223456789123456789",
                "house_id": "123456789123456789",
                "emoji": None,
                "description": None,
                "default_permission_override": None
            }],
            "roles": [],
            "owner_id": "323456789123456789",
            "name": "house",
            "members": [{
                "user_id": "323456789123456789",
                "user": {
                    "username": "username",
                    "user_flags": 2,
                    "name": "name",
                    "id": "323456789123456789",
                    "icon": None,
                    "header": None,
                    "presence": "online",
                    "bot": False
                },
                "roles": [],
                "last_permission_update": None,
                "joined_at": "1970-01-01T00:00:0.000Z",
                "house_id": "123456789123456789"
            }],
            "id": "123456789123456789",
            "icon": None,
            "entities": [{
                "type": 1,
                "resource_pointers": [{
                    "resource_type": "room",
                    "resource_id": "223456789123456789"
                }],
                "position": 0,
                "name": "Rooms",
                "id": "423456789123456789"
            }],
            "default_permissions": 10000000,
            "banner": None
        }
        relationship_data = {
            "user_id": "223456789123456789",
            "user": {
                "username": "test",
                "user_flags": 2,
                "name": "test",
                "id": "423456789123456789",
                "icon": None,
                "header": None,
                "presence": "online"
            },
            "type": 3,
            "last_updated_at": "1970-01-01T00:00:0.000Z"
        }
        private_room_data = {
            "default_permission_override": None,
            "description": "test",
            "emoji": None,
            "house_id": None,
            "id": "523456789123456789",
            "last_message_id": None,
            "name": None,
            "owner_id": "423456789123456789",
            "permission_overrides": 10000000,
            "position": None,
            "recipients": [{
                "username": "test",
                "user_flags": 2,
                "name": "test",
                "id": "423456789123456789",
                "icon": None,
                "header": None,
                "presence": "online"
            }],
            "type": 1
        }
        private_group_room_data = {
            "default_permission_override": None,
            "description": "test",
            "emoji": None,
            "house_id": None,
            "id": "623456789123456789",
            "last_message_id": None,
            "name": None,
            "owner_id": "423456789123456789",
            "permission_overrides": 10000000,
            "position": None,
            "recipients": [
                {
                    "username": "username",
                    "user_flags": 2,
                    "name": "name",
                    "id": "323456789123456789",
                    "icon": None,
                    "header": None,
                    "presence": "online",
                    "bot": False
                },
                {
                    "username": "test",
                    "user_flags": 2,
                    "name": "test",
                    "id": "423456789123456789",
                    "icon": None,
                    "header": None,
                    "presence": "online"
                }
            ],
            "type": 2
        }

        client = openhivenpy.HivenClient()
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
