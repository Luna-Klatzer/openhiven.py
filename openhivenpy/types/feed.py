import logging
import fastjsonschema
from .. import utils

from . import HivenObject, check_valid
from ..exceptions import InvalidPassedDataError, InitializationError
logger = logging.getLogger(__name__)

__all__ = ['Feed']


class Feed(HivenObject):
    """ Represents the feed that is displayed on Hiven """
    def __init__(self, **kwargs):
        pass

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('unknown', "")
        ]
        return '<Feed {}>'.format(' '.join('%s=%s' % t for t in info))
