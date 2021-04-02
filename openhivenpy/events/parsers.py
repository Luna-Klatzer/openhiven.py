import logging
import typing

__all__ = ['HivenParsers']

from openhivenpy.gateway import DynamicEventBuffer
from openhivenpy import types

logger = logging.getLogger(__name__)


class HivenParsers:
    """ Event Parsers for Hiven Events that validate and update the cached data """
    def __init__(self, client):
        self.client = client

    @property
    def storage(self) -> typing.Union[None, dict]:
        return getattr(self.client, 'storage', None)

    async def dispatch(self, event: str, data: dict) -> typing.Tuple[list, dict]:
        """
        Dispatches the parser and returns the args and kwargs

        :param event: Event name that should be called
        :param data: Raw WebSocket Data that should be passed
        :return: The args and kwargs that were created with the parser
        """
        coro = getattr(self, 'on_' + event.lower().replace('on_', ''), None)

        if callable(coro):
            return await coro(data)
        else:
            logger.warning(f"[EVENTS] Parser for event {event} was not found!")

    # Implementation of parsers that handle the events and add to the buffer the args and kwargs for the event listeners

    async def on_user_update(self, data):
        buffer: DynamicEventBuffer = self.client.message_broker.get_buffer('user_update')

        user_data = types.User.form_object(self.storage['users'][data['id']])
        user = await types.User.create_from_dict(user_data, self.client)

        user_data = types.User.form_object(data)
        new_user = await types.User.create_from_dict(user_data, self.client)

        self.storage['users'][data['id']].update(data)

        # Parameter that will be passed to the listener
        args = (user, new_user)
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_join(self, data):
        buffer = self.client.message_broker.get_buffer('house_join')

        # Parameter that will be passed to the assigned listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_remove(self, data):
        buffer = self.client.message_broker.get_buffer('house_remove')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_update(self, data):
        buffer = self.client.message_broker.get_buffer('house_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_delete(self, data):
        buffer = self.client.message_broker.get_buffer('house_delete')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_downtime(self, data):
        buffer = self.client.message_broker.get_buffer('house_downtime')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_room_create(self, data):
        buffer = self.client.message_broker.get_buffer('room_create')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_room_update(self, data):
        buffer = self.client.message_broker.get_buffer('room_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_room_delete(self, data):
        buffer = self.client.message_broker.get_buffer('room_delete')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_member_join(self, data):
        buffer = self.client.message_broker.get_buffer('house_member_join')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_member_leave(self, data):
        buffer = self.client.message_broker.get_buffer('house_member_leave')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_member_enter(self, data):
        buffer = self.client.message_broker.get_buffer('house_member_enter')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_member_update(self, data):
        buffer = self.client.message_broker.get_buffer('house_member_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_member_exit(self, data):
        buffer = self.client.message_broker.get_buffer('house_member_exit')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_member_update(self, data):
        buffer = self.client.message_broker.get_buffer('member_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_member_chunk(self, data):
        buffer = self.client.message_broker.get_buffer('house_member_chunk')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_batch_house_member_update(self, data):
        buffer = self.client.message_broker.get_buffer('batch_house_member_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_house_entity_update(self, data):
        buffer = self.client.message_broker.get_buffer('house_entity_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_relationship_update(self, data):
        buffer = self.client.message_broker.get_buffer('relationship_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_presence_update(self, data):
        buffer = self.client.message_broker.get_buffer('presence_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_message_create(self, data):
        buffer = self.client.message_broker.get_buffer('message_create')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_message_update(self, data):
        buffer = self.client.message_broker.get_buffer('message_update')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_message_delete(self, data):
        buffer = self.client.message_broker.get_buffer('message_delete')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs

    async def on_typing_start(self, data):
        buffer = self.client.message_broker.get_buffer('typing_start')
        # Parameter that will be passed to the listener
        args = ()
        kwargs = {}
        buffer.add(data, args, kwargs)
        return args, kwargs
