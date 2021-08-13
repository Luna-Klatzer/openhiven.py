import openhivenpy

token_ = ""
client = openhivenpy.HivenClient()


def test_start(token):
    global token_
    token_ = token


class TestEntity:
    def test_preparation(self):
        client.storage.update_client_user({
            "username": "username",
            "flags": 2,
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
                    "flags": 2,
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
        })

    def test_init(self):
        data = {
            "house_id": "123456789123456789",
            "type": 1,
            "resource_pointers": [{
                "resource_type": "room",
                "resource_id": "223456789123456789"
            }],
            "position": 0,
            "name": "Rooms",
            "id": "423456789123456789"
        }
        openhivenpy.Entity.format_obj_data(data)
        entity = openhivenpy.Entity(data, client)

        assert entity._house == data['house_id']
        assert entity.house.id == data['house_id']
        assert entity.resource_pointers[0].id == data['resource_pointers'][0]['resource_id']
        assert entity.house.owner.id == entity.house.owner_id
