import openhivenpy
import asyncio


class TestCache:
    test_house_args = {
        'rooms': [
            {
                'type': 0,
                'recipients': None,
                'position': 0,
                'permission_overrides': None,
                'owner_id': None,
                'name': 'General',
                'last_message_id': '212317519447324904',
                'id': '212317516322568423',
                'house_id': '212317516322568422',
                'emoji': None,
                'description': None,
                'default_permission_override': None
            }
        ],
        'roles': [],
        'owner_id': '175697072878514388',
        'name': 'A pretty good House',
        'members': [
            {
                'user_id': '175697072878514388',
                'user': {
                    'username': 'kudo',
                    'user_flags': '0',
                    'name': 'The lovely Kudo',
                    'id': '175697072878514388',
                    'icon': '7b33d7197e7a7f4cdf5e8b0ec3e0a1fcd0620b06.png',
                    'header': '0aa06362a7ac3709d063c15df3b15055003e6bf8.png',
                    'bot': False
                },
                'roles': None,
                'presence': 'online',
                'last_permission_update': None,
                'joined_at': '2021-02-12T21:14:00.561Z',
                'id': '175697072878514388',
                'house_id': '212317516322568422'
            }
        ],
        'id': '212317516322568422',
        'icon': None,
        'entities': [
            {
                'type': 1,
                'resource_pointers': [
                    {
                        'resource_type': 'room',
                        'resource_id': '212317516322568423'
                    }
                ],
                'position': 0,
                'name': 'Rooms',
                'id': '212317516473562181',
                'house_id': '212317516322568422'
            },
            {
                'type': 1,
                'resource_pointers': None,
                'position': 1,
                'name': 'stuff',
                'id': '212317521896798165',
                'house_id': '212317516322568422'
            }
        ],
        'default_permissions': 131139,
        'banner': None
    }

    def test_init(self):
        cache = openhivenpy.client.ClientCache("", False)
        assert cache['token'] == ""
        assert cache['log_ws_output'] is False
        assert cache['houses'] == {}
        assert cache['house_ids'] == []
        assert cache['settings'] == {}
        assert cache['read_state'] == {}

    def test_add_house(self):
        cache = openhivenpy.client.ClientCache("", False)
        cache.add_or_update_house(self.test_house_args)
        assert cache['houses'][self.test_house_args['id']] == self.test_house_args

