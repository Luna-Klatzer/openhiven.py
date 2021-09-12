import fastjsonschema

import openhivenpy
from openhivenpy import Embed


class TestEmbed:
    def test_simple_init(self):
        data = {
            'url': "https://link-image/stuff",
            'type': 2,
            'image': "https://link-image/stuff.png",
            'description': "Description",
            'title': "Test"
        }
        data = Embed.validate(data)
        client = openhivenpy.UserClient()
        obj = Embed(data, client)

        assert obj.url == data['url']
        assert obj.type == data['type']
        assert obj.image == data['image']
        assert obj.description == data['description']
        assert obj.title == data['title']

    def test_missing_data(self):
        try:
            Embed.validate({
                'type': 2,
                'url': ""
            })
        except fastjsonschema.exceptions.JsonSchemaValueException:
            pass
        else:
            assert False

        try:
            Embed.validate({
                'url': ""
            })
        except fastjsonschema.exceptions.JsonSchemaValueException:
            pass
        else:
            assert False

    def test_wrong_data_type(self):
        try:
            Embed.validate({
                'url': "https://link-image/stuff",
                'type': "x",
                'image': "https://link-image/stuff.png",
                'description': "Description",
                'title': "Test"
            })
        except fastjsonschema.exceptions.JsonSchemaValueException:
            pass
        else:
            assert False

        try:
            Embed.validate({
                'type': 2,
                'image': "https://link-image/stuff.png",
                'title': 3
            })
        except fastjsonschema.exceptions.JsonSchemaValueException:
            pass
        else:
            assert False

    def test_additional_data(self):
        data = {
            'type': 2,
            'image': "https://link-image/stuff.png",
            'title': "Test",
            'additional': {}
        }
        # Additional data will be ignored while validating since it won't be inherited at the class instance creation

        try:
            Embed.validate(data)
        except fastjsonschema.exceptions.JsonSchemaValueException:
            pass
        else:
            assert False

    def test_format_obj_data(self):
        _input = {
            'url': "https://link-image/stuff",
            'type': 2,
            'image': "https://link-image/stuff.png",
            'description': "Description",
            'title': "Test"
        }
        data = Embed.format_obj_data(_input)
        assert data['url'] == _input['url']
        assert data['type'] == _input['type']
        assert data['image'] == _input['image']
        assert data['description'] == _input['description']
        assert data['title'] == _input['title']

        client = openhivenpy.UserClient()
        obj = Embed(data, client)

        assert obj.url == data['url']
        assert obj.type == data['type']
        assert obj.image == data['image']
        assert obj.description == data['description']
        assert obj.title == data['title']
