# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging

from . import HivenTypeObject

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['Feed']


class Feed(HivenTypeObject):
    """ Represents the feed that is displayed on Hiven specifically for the user """
    def __init__(self, data: dict, client: HivenClient):
        pass

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('unknown', "")
        ]
        return '<Feed {}>'.format(' '.join('%s=%s' % t for t in info))
