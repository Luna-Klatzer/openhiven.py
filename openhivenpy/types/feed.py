import logging
from marshmallow import Schema, fields, post_load, ValidationError, EXCLUDE
from .. import utils

from . import HivenObject
from ..exception import InvalidPassedDataError, InitializationError
logger = logging.getLogger(__name__)

__all__ = ['Feed']


class Feed(HivenObject):
    """
    Represents the feed that is displayed on Hiven

    Deprecated and will likely get removed in future releases
    """
    def __init__(self, **kwargs):
        pass

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('unknown', "")
        ]
        return '<Feed {}>'.format(' '.join('%s=%s' % t for t in info))
