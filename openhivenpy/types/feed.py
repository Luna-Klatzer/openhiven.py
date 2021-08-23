# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from ..base_types import DataClassObject

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['Feed']


class Feed(DataClassObject):
    """
    Represents the feed that is displayed on Hiven specifically for the user
    """

    def __init__(self, data: dict, client: HivenClient):
        super().__init__()

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('unknown', "")
        ]
        return '<Feed {}>'.format(' '.join('%s=%s' % t for t in info))
