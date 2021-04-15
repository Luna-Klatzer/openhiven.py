import openhivenpy

token_ = ""
client = openhivenpy.HivenClient()


def test_start(token):
    global token_
    token_ = token


class TestHouse:
    data = {
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

    def test_preparation(self):
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

    def test_init(self):
        client.storage.add_or_update_house(self.data)
        house = client.get_house(self.data['id'])
        user = client.get_user(self.data['owner_id'])
        entity = client.get_entity(self.data['entities'][0]['id'])

        assert house.id == self.data['id']
        assert house.owner.id == user.id
        assert house.entities[0].id == entity.id
        assert house.members[0].id == client.id
        assert house.users[0].id == client.id

