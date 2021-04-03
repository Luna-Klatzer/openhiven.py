import logging

from . import HivenObject

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
