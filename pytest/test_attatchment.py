import fastjsonschema

from openhivenpy.types import Attachment


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
        data = Attachment.validate(data)
        obj = Attachment(**data)

        assert obj.filename == data['filename']
        assert obj.media_url == data['media_url']
        assert obj.raw == data['raw']
