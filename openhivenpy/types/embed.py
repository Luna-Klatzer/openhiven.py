"""
Embed File which implements the Hiven Embed type

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
from typing import Optional
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from .hiven_type_schemas import EmbedSchema, get_compiled_validator
from ..base_types import DataClassObject
from ..utils import log_type_exception

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['Embed']


class Embed(DataClassObject):
    """
    Represents an embed message object.

    This can represent an either customised embed or fetched embed from a
    website
    """
    _json_schema: dict = EmbedSchema
    json_validator = get_compiled_validator(_json_schema)

    @log_type_exception('Embed')
    def __init__(self, data: dict, client: HivenClient):
        """
        Represents an embed message object either customised or from a website

        :param data: Data that should be used to create the object
        :param client: The HivenClient
        """
        super().__init__()
        self._url = data.get('url')
        self._type = data.get('type')
        self._title = data.get('title')
        self._image = data.get('image')
        self._description = data.get('description')
        self._client = client

    @classmethod
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be
        required for the creation of an instance.

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a 
        new class instance
        """
        return cls.validate(data)

    @property
    def url(self) -> Optional[str]:
        """ The URL of the embed, if it's a web embed """
        return getattr(self, '_url', None)

    @property
    def type(self) -> Optional[int]:
        """ The type of the Embed """
        return getattr(self, '_type', None)

    @property
    def title(self) -> Optional[str]:
        """ The title of the embed """
        return getattr(self, '_title', None)

    @property
    def image(self) -> Optional[str]:
        """ The URL to the image of the embed """
        return getattr(self, '_image', None)

    @property
    def description(self) -> Optional[str]:
        """ The description of the embed, if it has one """
        return getattr(self, '_description', None)
