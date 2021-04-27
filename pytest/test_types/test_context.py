import time

import openhivenpy

token_ = ""
client = openhivenpy.HivenClient()


def test_start(token):
    global token_
    token_ = token


class TestContext:
    def test_preparations(self):
        client.storage.update_client_user({
            "username": "username",
            "user_flags": 2,
            "name": "name",
            "id": '323456789123456789',
            "icon": None,
            "header": None,
            "presence": "online",
            "bot": False
        })
        client.storage.add_or_update_house({
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
            "entities": [],
            "default_permissions": 10000000,
            "banner": None
        })

    def test_init(self):
        self.test_preparations()
        data = {
            "room": {
                "type": 0,
                "recipients": None,
                "position": 2,
                "permission_overrides": None,
                "owner_id": None,
                "name": "room",
                "last_message_id": None,
                "id": '223456789123456789',
                "house_id": '123456789123456789',
                "emoji": None,
                "description": None,
                "default_permission_override": None
            },
            "author": {
                "username": "username",
                "user_flags": 2,
                "name": "name",
                "id": '323456789123456789',
                "icon": None,
                "header": None,
                "presence": "online",
                "bot": False
            },
            "house": {
                "owner_id": '323456789123456789',
                "name": "house",
                "id": '123456789123456789',
                "icon": None,
                "default_permissions": 10000000,
                "banner": None
            },
            "timestamp": round(time.time())
        }
        openhivenpy.Context.format_obj_data(data)
        context = openhivenpy.Context(data, client)

        assert context._author == data['author_id']
        assert context._house == data['house_id']
        assert context._room == data['room_id']

        assert context.author.id == data['author_id']
        assert context.house.id == data['house_id']
        assert context.room.id == data['room_id']

        assert context._author.id == data['author_id']
        assert context._house.id == data['house_id']
        assert context._room.id == data['room_id']
