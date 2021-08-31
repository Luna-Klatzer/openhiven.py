"""
Feed File which implements the Hiven Feed type, which should contain social
media information of a specific user and their linked acccounts.

---

Under MIT License

Copyright © 2020 - 2021 Luna Klatzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from ..base_types import DataClassObject
from ..utils import log_type_exception

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['Feed']


class Feed(DataClassObject):
    """
    Represents the feed that is displayed on Hiven specifically for the user
    """

    @log_type_exception('Feed')
    def __init__(self, data: dict, client: HivenClient):
        super().__init__()

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('unknown', "")
        ]
        return '<Feed {}>'.format(' '.join('%s=%s' % t for t in info))
