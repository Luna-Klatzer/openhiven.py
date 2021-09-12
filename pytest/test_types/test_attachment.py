import fastjsonschema

import openhivenpy
from openhivenpy import Attachment


class TestAttachment:
    def test_simple_init(self):
        data = {
            'filename': 'test',
            'media_url': 'test',
            'raw': {}
        }
        data = Attachment.validate(data)
        client = openhivenpy.UserClient()
        obj = Attachment(data, client)

        assert obj.filename == data['filename']
        assert obj.media_url == data['media_url']
        assert obj.raw == data['raw']

    def test_missing_data(self):
        try:
            Attachment.validate({
                'filename': 'test',
                'raw': {}
            })
        except fastjsonschema.exceptions.JsonSchemaValueException:
            pass
        else:
            assert False

        try:
            Attachment.validate({
                'raw': {}
            })
        except fastjsonschema.exceptions.JsonSchemaValueException:
            pass
        else:
            assert False

    def test_wrong_data_type(self):
        try:
            Attachment.validate({
                'filename': 2,
                'media_url': '2',
                'raw': {}
            })
        except fastjsonschema.exceptions.JsonSchemaValueException:
            pass
        else:
            assert False

        try:
            Attachment.validate({
                'filename': 2,
                'media_url': '2',
                'raw': {}
            })
        except fastjsonschema.exceptions.JsonSchemaValueException:
            pass
        else:
            assert False

    def test_additional_data(self):
        data = {
            'filename': 'test',
            'media_url': 'test',
            'raw': {},
            'additional': {}
        }
        # Additional data will be ignored while validating since it won't be inherited at the class instance creation

        try:
            Attachment.validate(data)
        except fastjsonschema.exceptions.JsonSchemaValueException:
            pass
        else:
            assert False

    def test_format_obj_data(self):
        _input = {
            'filename': 'test',
            'media_url': 'test',
            'raw': {},
        }
        data = Attachment.format_obj_data(_input)
        assert data['raw'].get('raw', None) is None
        assert data == {
            **_input,
            'raw': {
                'filename': 'test',
                'media_url': 'test',
            }
        }

        client = openhivenpy.UserClient()
        obj = Attachment(data, client)
        assert obj.filename == _input['filename']
        assert obj.media_url == _input['media_url']
