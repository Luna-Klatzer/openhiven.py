import logging
from marshmallow import Schema, fields, post_load, ValidationError, RAISE

from . import HivenObject

logger = logging.getLogger(__name__)

__all__ = ['Presence']


class Presence(HivenObject):
    """
    Represents a User Presence

    Deprecated! Will be removed in v0.1.3
    """
    def __init__(self, data: dict, user, http):
        self._http = http
        self._user = user
        self._presence = data.get('presence')

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('presence', self.presence),
            ('user', repr(self.user))
        ]
        return '<Presence {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def user(self):
        return self._user

    @property
    def presence(self):
        return self._presence
