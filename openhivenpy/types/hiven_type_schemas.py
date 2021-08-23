""" Schemas for the type classes """
import fastjsonschema


def get_compiled_validator(_json_schema: dict) -> dict:
    """
    Gets the compiled validator for the passed schema
    """
    return fastjsonschema.compile(_json_schema)


AttachmentSchema: dict = {
    'type': 'object',
    'properties': {
        'filename': {'type': 'string'},
        'media_url': {'type': 'string'},
        'raw': {
            'type': 'object',
            'default': {}
        },
    },
    'additionalProperties': False,
    'required': ['filename', 'media_url']
}

ContextSchema: dict = {
    'type': 'object',
    'properties': {
        'room': {'type': 'object'},
        'author': {'type': 'object'},
        'timestamp': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'integer'}
            ],
        },
        'house': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'null'}
            ]
        },
    },
    'additionalProperties': False,
    'required': ['room', 'author', 'timestamp']
}

EmbedSchema: dict = {
    'type': 'object',
    'properties': {
        'url': {'type': 'string', 'default': None},
        'type': {'type': 'integer'},
        'title': {'type': 'string'},
        'image': {'type': 'string', 'default': None},
        'description': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        }
    },
    'additionalProperties': False,
    'required': ['type', 'title']
}

EntitySchema: dict = {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'name': {'type': 'string'},
        'type': {'type': 'integer', 'default': 1},
        'resource_pointers': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'array'},
                {'type': 'null'},
            ],
            'default': []
        },
        'house_id': {'type': 'string'},
        'house': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'string'},
                {'type': 'null'},
            ]
        },
        'position': {'type': 'integer'}
    },
    'additionalProperties': False,
    'required': ['id', 'name', 'position', 'resource_pointers', 'house_id']
}

FeedSchema: dict = {}

LazyHouseSchema: dict = {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'name': {'type': 'string'},
        'icon': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
        },
        'owner_id': {'type': 'string'},
        'owner': {'default': None},
        'rooms': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'array'},
                {'type': 'null'}
            ],
            'default': {}
        },
        'type': {
            'anyOf': [
                {'type': 'integer'},
                {'type': 'null'}
            ],
        },
        'client_member': {
            'anyOf': [
                {'type': 'integer'},
                {'type': 'string'},
                {'type': 'object'},
                {'type': 'null'}
            ],
        },
    },
    'required': ['id', 'name', 'owner_id']
}

HouseSchema: dict = {
    'type': 'object',
    'properties': {
        **LazyHouseSchema['properties'],
        'entities': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'array'},
                {'type': 'null'}
            ],
            'default': {}
        },
        'members': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'array'},
                {'type': 'null'}
            ],
            'default': {}
        },
        'roles': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'array'},
                {'type': 'null'}
            ],
            'default': {},
        },
        'banner': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None,
        },
        'default_permissions': {
            'anyOf': [
                {'type': 'integer'},
                {'type': 'null'}
            ],
            'default': None,
        }
    },
    'additionalProperties': False,
    'required': [*LazyHouseSchema['required'], 'entities', 'members', 'roles']
}

InviteSchema: dict = {
    'type': 'object',
    'properties': {
        'code': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
        },
        'url': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
        },
        'created_at': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'house_id': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'blocked': {
            'anyOf': [
                {'type': 'boolean'},
                {'type': 'null'}
            ],
            'default': None
        },
        'max_age': {
            'anyOf': [
                {'type': 'integer'},
                {'type': 'null'}
            ],
            'default': None
        },
        'max_uses': {
            'anyOf': [
                {'type': 'integer'},
                {'type': 'null'}
            ],
            'default': None
        },
        'mfa_enabled': {
            'anyOf': [
                {'type': 'boolean'},
                {'type': 'null'}
            ],
            'default': None
        },
        'type': {
            'type': 'integer',
            'default': None
        },
        'house_members': {
            'type': 'integer',
            'default': None
        }
    },
    'additionalProperties': False,
    'required': ['code']
}

MentionSchema: dict = {
    'type': 'object',
    'properties': {
        'timestamp': {'type': 'string'},
        'user': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'null'}
            ],
        },
        'author': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'null'}
            ],
        },
    },
    'additionalProperties': False,
    'required': ['timestamp', 'user', 'author']
}

DeletedMessageSchema: dict = {
    'type': 'object',
    'properties': {
        'message_id': {'type': 'string'},
        'house_id': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'room_id': {'type': 'string'}
    },
    'additionalProperties': False,
    'required': ['message_id', 'room_id']
}

MessageSchema: dict = {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'author': {'type': 'object'},
        'author_id': {'type': 'string'},
        'attachment': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'null'}
            ],
            'default': {},
        },
        'content': {'type': 'string'},
        'timestamp': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'integer'}
            ],
        },
        'edited_at': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'mentions': {
            'type': 'array',
            'default': []
        },
        'type': {'type': 'integer'},
        'exploding': {
            'anyOf': [
                {'type': 'boolean'},
                {'type': 'null'}
            ],
            'default': None
        },
        'house_id': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'room_id': {'type': 'string'},
        'embed': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'null'}
            ],
            'default': None
        },
        'bucket': {
            'anyOf': [
                {'type': 'integer'},
                {'type': 'null'}
            ],
            'default': None
        },
        'device_id': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'integer'},
                {'type': 'null'}
            ],
            'default': None
        },
        'exploding_age': {'default': None}
    },
    'additionalProperties': False,
    'required': ['id', 'author', 'author_id', 'content', 'timestamp', 'type', 'mentions', 'room_id']
}


PrivateRoomSchema: dict = {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'last_message_id': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'},
            ],
            'default': None
        },
        'recipients': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'array'},
                {'type': 'null'}
            ],
            'default': {},
        },
        'name': {'default': None},
        'description': {'default': None},
        'emoji': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'null'}
            ],
            'default': None
        },
        'type': {'type': 'integer'},
        'permission_overrides': {'default': None},
        'default_permission_override': {'default': None},
        'position': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'integer'},
                {'type': 'null'}
            ],
            'default': None
        },
        'owner_id': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'house_id': {'type': 'null'}  # weird hiven bug
    },
    'additionalProperties': False,
    'required': ['id', 'recipients', 'type']
}

RelationshipSchema: dict = {
    'type': 'object',
    'properties': {
        'user_id': {'type': 'string'},
        'user': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'object'},
                {'type': 'null'}
            ],
        },
        'type': {'type': 'integer'},
        'last_updated_at': {'type': 'string'}
    },
    'additionalProperties': False,
    'required': ['user_id', 'type']
}

TextRoomSchema: dict = {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'name': {'type': 'string'},
        'house_id': {'type': 'string'},
        'position': {'type': 'integer'},
        'type': {'type': 'integer'},
        'emoji': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'null'}
            ],
            'default': None
        },
        'description': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'last_message_id': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'house': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'object'},
                {'type': 'null'}
            ],
        },
        'permission_overrides': {'default': None},
        'default_permission_override': {'default': None},
        'recipients': {'default': None},
        'owner_id': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
    },
    'additionalProperties': False,
    'required': ['id', 'name', 'house_id', 'type']
}

LazyUserSchema: dict = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'name': {'type': 'string'},
        'id': {'type': 'string'},
        'flags': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'integer'},
                {'type': 'null'}
            ],
            'default': None
        },
        'user_flags': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'integer'},
                {'type': 'null'}
            ],
            'default': None
        },
        'bio': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'email_verified': {
            'anyOf': [
                {'type': 'boolean'},
                {'type': 'null'}
            ],
            'default': None
        },
        'header': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'icon': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'bot': {
            'anyOf': [
                {'type': 'boolean'},
                {'type': 'string'},  # TODO! Needs to be removed when the string bug disappeared
                {'type': 'null'}
            ],
            'default': False
        },
        'account': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'integer'},
                {'type': 'null'}
            ],
        },
        'application': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
        }
    },
    'required': ['username', 'name', 'id']
}

UserSchema: dict = {
    'type': 'object',
    'properties': {
        **LazyUserSchema['properties'],
        'location': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'website': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'presence': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'email': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'null'}
            ],
            'default': None
        },
        'blocked': {
            'anyOf': [
                {'type': 'boolean'},
                {'type': 'null'}
            ],
            'default': None
        },
        'mfa_enabled': {
            'anyOf': [
                {'type': 'boolean'},
                {'type': 'null'}
            ],
            'default': None
        },
    },
    'additionalProperties': False,
    'required': [*LazyUserSchema['required']]
}

MemberSchema: dict = {
    'type': 'object',
    'properties': {
        **UserSchema['properties'],
        'user_id': {'type': 'string'},
        'house': {},
        'house_id': {'type': 'string'},
        'joined_at': {'type': 'string'},
        'roles': {
            'anyOf': [
                {'type': 'object'},
                {'type': 'array'},
                {'type': 'null'}
            ],
            'default': {},
        },
        'user': {'type': 'object'},
        'last_permission_update': {'default': None}
    },
    'additionalProperties': False,
    'required': ['user', 'user_id', 'house_id', 'joined_at']
}