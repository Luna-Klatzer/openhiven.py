import logging
import sys

import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTP
from ._get_type import getType

logger = logging.getLogger(__name__)

__all__ = ['Entity']


class Entity:
    """`openhivenpy.types.Category`

    Data Class for a Category/Entity
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Represents a Hiven Entity

    """

    def __init__(self, data: dict, http: HTTP):
        try:
            self._type = data.get('type', 1)
            self._position = data.get('position')
            self._resources = []

            if data.get('resource_pointers'):
                for r in data.get('resource_pointers', []):
                    self._resources.append(r)

            self._name = data.get('name')
            self._id = data.get('id')
            self._house_id = data.get('house_id')
            self._http = http

        except AttributeError as e:
            logger.error(f"[CATEGORY] Failed to initialize the Category object! "
                         f"> {sys.exc_info()[0].__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize the Category object! Most likely faulty data! "
                                            f"> {sys.exc_info()[0].__name__}, {str(e)}")

        except Exception as e:
            logger.error(f"[CATEGORY] Failed to initialize the Category object! "
                         f"> {sys.exc_info()[0].__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize the Category object! Possibly faulty data! "
                                            f"> {sys.exc_info()[0].__name__}, {str(e)}")

    def __str__(self) -> str:
        return str(repr(self))

    def __repr__(self) -> str:
        info = [
            ('name', self.name),
            ('id', self.id),
            ('position', self.position),
            ('type', self.type)
        ]
        return '<Category {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def type(self) -> int:
        return self._type

    @property
    def resources(self) -> list:
        return self._resources

    @property
    def name(self) -> list:
        return self._name

    @property
    def id(self) -> list:
        return self._id

    @property
    def house_id(self) -> list:
        return self._house_id

    @property
    def position(self) -> int:
        return self._position
