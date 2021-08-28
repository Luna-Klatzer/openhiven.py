"""
Event parsers which handle events, validate and form data and add an event to
the buffer
"""
from __future__ import annotations

import logging
from copy import deepcopy
from typing import Optional, Tuple, TYPE_CHECKING, Dict

from .. import types
from ..base_types import HivenObject
from ..gateway import DynamicEventBuffer

if TYPE_CHECKING:
    from ..client import HivenClient
    from ..client import ClientCache

__all__ = [
    'HivenParsers',
    'format_event_as_listener'
]

logger = logging.getLogger(__name__)


def format_event_as_listener(event: str) -> str:
    """
    Formats the passed event as an listener function in the following style:

        on_<lowercase_event_name>

    """
    return 'on_' + event.lower().replace('on_', '')


class HivenParsers(HivenObject):
    """
    Event Parsers for Hiven Events that validate and update the cached data
    """

    def __init__(self, client):
        self.client: HivenClient = client

    @property
    def storage(self) -> Optional[ClientCache]:
        """ Returns the cached storage """
        return getattr(self.client, 'storage', None)

    def _get_from_client_buffer(
            self,
            event: str,
            args: Optional[tuple] = None,
            kwargs: Optional[dict] = None
    ):
        return self.client.message_broker.get_buffer(
            event,
            args,
            kwargs
        )

    async def dispatch(self, event: str, data: dict) -> Tuple[list, dict]:
        """
        Dispatches the parser and returns the args and kwargs. Note that this
        will only add the event to the buffer and NOT execute it. The asyncio
        event loop will run it as soon as the

        :param event: Event name that should be called
        :param data: Raw WebSocket Data that should be passed
        :return: The args and kwargs that were created with the parser
        """
        # getting the method from self
        coro = getattr(self, format_event_as_listener(event), None)

        if callable(coro):
            new_data: dict = deepcopy(data)
            return await coro(new_data)
        else:
            logger.warning(f"[EVENTS] Parser for event {event} was not found!")

    # Implementation of parsers that handle the events and add to the buffer
    # the args and kwargs for the event listeners

    async def on_user_update(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: USER_UPDATE """
        old_user_data = self.storage['users'][data['id']]  # cached data
        old_user = types.User(old_user_data, self.client)

        user_data = self.storage.add_or_update_user(data)
        new_user = types.User(user_data, self.client)

        # Parameter that will be passed to the assigned listener
        args: Tuple[types.User, types.User] = (old_user, new_user)
        kwargs: Dict = {}

        buffer: DynamicEventBuffer = self._get_from_client_buffer(
            'user_update'
        )
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_join(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: HOUSE_JOIN """
        self.storage.add_or_update_house(data)

        new_house_data = types.House.format_obj_data(data)
        new_house = types.House(new_house_data, self.client)

        # Parameter that will be passed to the assigned listener
        args: Tuple[types.House] = \
            tuple([new_house])  # avoiding warning bc of singular tuple item
        kwargs: Dict = {}

        buffer = self._get_from_client_buffer('house_join')
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_update(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: HOUSE_UPDATE """
        old_house_data = self.storage['houses'][data['id']]
        old_house = types.House(old_house_data, self.client)

        new_house_data = self.storage.add_or_update_house(data)
        new_house = types.House(new_house_data, self.client)

        # Parameter that will be passed to the assigned listener
        args: Tuple[types.House, types.House] = (old_house, new_house)
        kwargs: Dict = {}

        buffer = self._get_from_client_buffer('house_update')
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_down(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: HOUSE_DOWN

        Both for py-events house_down and house_delete.

        If property unavailable of the data is *false* it's a deleted house.
        """
        if data.get('unavailable') is True:
            buffer = self._get_from_client_buffer('house_down')
        else:
            buffer = self._get_from_client_buffer('house_delete')
            self.storage.remove_house(data['house_id'])

        # Parameter that will be passed to the assigned listener
        args: Tuple = tuple([data['house_id']])
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_leave(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: HOUSE_LEAVE """
        self.storage.remove_house(data['house_id'])

        # Parameter that will be passed to the assigned listener
        args: Tuple = tuple([data['house_id']])
        kwargs: Dict = {}

        buffer = self._get_from_client_buffer('house_leave')
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_room_create(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: ROOM_CREATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('room_create')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_room_update(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: ROOM_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('room_update')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_room_delete(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: ROOM_DELETE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('room_delete')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_join(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: HOUSE_MEMBER_JOIN

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_join')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_leave(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: HOUSE_MEMBER_LEAVE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_leave')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_enter(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: HOUSE_MEMBER_ENTER

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_enter')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_update(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: HOUSE_MEMBER_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_update')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_exit(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: HOUSE_MEMBER_EXIT

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_exit')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_chunk(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: HOUSE_MEMBER_CHUNK

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_chunk')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_batch_house_member_update(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: BATCH_HOUSE_MEMBER_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('batch_house_member_update')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_entity_update(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: HOUSE_ENTITY_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_entity_update')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_relationship_update(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: RELATIONSHIP_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('relationship_update')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_presence_update(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: PRESENCE_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('presence_update')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_message_create(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: MESSAGE_CREATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('message_create')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_message_update(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: MESSAGE_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('message_update')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_message_delete(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: MESSAGE_DELETE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('message_delete')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_typing_start(self, data: dict) -> Tuple[Tuple, Dict]:
        """ EVENT: TYPING_START

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('typing_start')
        # Parameter that will be passed to the assigned listener
        args: Tuple = ()
        kwargs: Dict = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs
