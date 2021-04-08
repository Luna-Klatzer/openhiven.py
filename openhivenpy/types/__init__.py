"""

Module for all data classes that represent Hiven Objects.

---

Under MIT License

Copyright © 2020 - 2021 Nicolas Klatzer

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

import typing
import inspect
from functools import wraps

from .. import utils

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import HivenClient

__all__ = [
    'check_valid',
    'Room',
    'LazyHouse', 'House',
    'PrivateRoom', 'PrivateGroupRoom',
    'LazyUser', 'User',
    'Message', 'DeletedMessage',
    'Context',
    'Member',
    'UserTyping',
    'Attachment',
    'Feed',
    'Entity',
    'Invite',
    'Mention',
    'Embed',
    'Relationship'
]


def check_valid(func: typing.Callable = None) -> typing.Callable:
    """
    Adds an additional try-except clause for logging and exception handling

    :param func: Function that should be wrapped
    """

    def decorator(func_: typing.Callable) -> typing.Any:
        @wraps(func_)
        def wrapper(*args, **kwargs):
            if inspect.iscoroutinefunction(func_):
                raise ValueError("Target of decorator must not be asynchronous")
            try:
                return func_(*args, **kwargs)
            except Exception:
                raise

        return wrapper  # func can still be used normally outside the event listening process

    if func is None:
        return decorator
    else:
        return decorator(func)


class HivenObject:
    """ Base Class for all Hiven Objects """
    _client: HivenClient = None

    @classmethod
    def validate(cls, data, *args, **kwargs) -> dict:
        try:
            return getattr(cls, 'json_validator')(data, *args, **kwargs)
        except Exception as e:
            utils.log_validation_traceback(cls, data, e)
            raise

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        # Automatically creating a list of tuples for all values
        info = [
            (attribute.replace('_', ''), value) if attribute != '_client' else None
            for attribute, value in self.__dict__.items()
        ]

        return '<{} {}>'.format(self.__class__.__name__, ' '.join('%s=%s' % t if t is not None else '' for t in info))


from .room import *
from .house import *
from .private_room import *
from .user import *
from .message import *
from .context import *
from .member import *
from .usertyping import *
from .attachment import *
from .feed import *
from .entity import *
from .invite import *
from .mention import *
from .embed import *
from .relationship import *
