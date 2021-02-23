import asyncio
import fastjsonschema

import openhivenpy
from openhivenpy.types import Attachment

token_ = ""


def test_start(token):
    global token_
    token_ = token


class TestAttachment:
    def test_simple_init(self):
        data = {
            'filename': 'test',
            'media_url': 'test',
            'raw': {}
        }
        data = Attachment.validate(data)
        obj = Attachment(**data)

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
            data = Attachment.validate(data)
        except fastjsonschema.exceptions.JsonSchemaValueException:
            pass
        else:
            assert False

    def test_form_object(self):
        input = {
            'filename': 'test',
            'media_url': 'test',
            'raw': {},
        }
        data = Attachment.form_object(input)
        assert data['raw'].get('raw', None) is None
        assert data == {
            **input,
            'raw': {
                'filename': 'test',
                'media_url': 'test',
            }
        }

        client = openhivenpy.UserClient(token_)
        obj = asyncio.run(Attachment.from_dict(data, client))
        assert obj.filename == input['filename']
        assert obj.media_url == input['media_url']
