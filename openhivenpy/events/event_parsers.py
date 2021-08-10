"""
Event parsers which handle events, validate and form data and add an event to
the buffer
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple, TYPE_CHECKING

from .. import types
from ..base_types import HivenObject
from ..gateway import DynamicEventBuffer

if TYPE_CHECKING:
    from ..client import HivenClient

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
    def storage(self) -> Optional[dict]:
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
            return await coro(data)
        else:
            logger.warning(f"[EVENTS] Parser for event {event} was not found!")

    # Implementation of parsers that handle the events and add to the buffer
    # the args and kwargs for the event listeners

    async def on_user_update(self, data) -> Tuple[tuple, dict]:
        """ EVENT: USER_UPDATE """
        buffer: DynamicEventBuffer = self._get_from_client_buffer(
            'user_update'
        )

        user_data = types.User.format_obj_data(
            self.storage['users'][data['id']]  # cached data
        )
        user = types.User(user_data, self.client)

        user_data = types.User.format_obj_data(data)
        new_user = types.User(user_data, self.client)

        self.storage['users'][data['id']].update(data)

        # Parameter that will be passed to the listener
        args = (user, new_user)
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_join(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_JOIN

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_join')

        # Parameter that will be passed to the assigned listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_remove(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_REMOVE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_remove')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_update(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_delete(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_DELETE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_delete')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_downtime(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_DOWNTIME

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_downtime')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_room_create(self, data) -> Tuple[tuple, dict]:
        """ EVENT: ROOM_CREATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('room_create')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_room_update(self, data) -> Tuple[tuple, dict]:
        """ EVENT: ROOM_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('room_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_room_delete(self, data) -> Tuple[tuple, dict]:
        """ EVENT: ROOM_DELETE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('room_delete')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_join(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_MEMBER_JOIN

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_join')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_leave(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_MEMBER_LEAVE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_leave')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_enter(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_MEMBER_ENTER

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_enter')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_update(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_MEMBER_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_exit(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_MEMBER_EXIT

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_exit')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_member_chunk(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_MEMBER_CHUNK

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_member_chunk')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_batch_house_member_update(self, data) -> Tuple[tuple, dict]:
        """ EVENT: BATCH_HOUSE_MEMBER_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('batch_house_member_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_house_entity_update(self, data) -> Tuple[tuple, dict]:
        """ EVENT: HOUSE_ENTITY_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('house_entity_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_relationship_update(self, data) -> Tuple[tuple, dict]:
        """ EVENT: RELATIONSHIP_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('relationship_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_presence_update(self, data) -> Tuple[tuple, dict]:
        """ EVENT: PRESENCE_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('presence_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_message_create(self, data) -> Tuple[tuple, dict]:
        """ EVENT: MESSAGE_CREATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('message_create')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_message_update(self, data) -> Tuple[tuple, dict]:
        """ EVENT: MESSAGE_UPDATE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('message_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_message_delete(self, data) -> Tuple[tuple, dict]:
        """ EVENT: MESSAGE_DELETE

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('message_delete')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs

    async def on_typing_start(self, data) -> Tuple[tuple, dict]:
        """ EVENT: TYPING_START

        No data passed at the moment. Gives empty args and kwargs
        """
        buffer = self._get_from_client_buffer('typing_start')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add_new_event(data, args, kwargs)
        return args, kwargs
