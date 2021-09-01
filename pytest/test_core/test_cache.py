import openhivenpy


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
                    'flags': '0',
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
        cache = openhivenpy.client.ClientCache(openhivenpy.HivenClient())
        assert cache['token'] == "undefined"
        assert cache['houses'] == {}
        assert cache['house_ids'] == []
        assert cache['settings'] == {}

    def test_update_client_user(self):
        data: dict = self.test_house_args['members'][0]['user']
        cache = openhivenpy.client.ClientCache(openhivenpy.HivenClient())
        cache.update_client_user(data)
        return_data = cache.update_client_user(data)

        validated_data = openhivenpy.User.format_obj_data(data)
        assert return_data == validated_data
        assert cache['client_user'] == validated_data
        assert cache['users'][data['id']] == validated_data

        return_data = cache.update_client_user(data)
        assert return_data == validated_data
        assert cache['client_user'] == validated_data
        assert cache['users'][data['id']] == validated_data

    def test_add_house(self):
        data = dict(self.test_house_args)
        cache = openhivenpy.client.ClientCache(openhivenpy.HivenClient())
        client_user = cache.update_client_user(dict(data['members'][0]['user']))
        return_data = cache.add_or_update_house(dict(data))

        # Regular format_obj_data won't add the client_user property!
        client_member = return_data.pop('client_member')
        assert return_data['members'][client_user['id']] == client_member

        validated_data = openhivenpy.House.format_obj_data(data)
        assert return_data == validated_data
        assert cache['houses'][self.test_house_args['id']] == return_data
