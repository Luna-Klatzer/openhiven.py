import logging
import typing

__all__ = ['HivenParsers']

logger = logging.getLogger(__name__)


class HivenParsers:
    """ Event Parsers for Hiven Events that validate and update the cached data """
    def __init__(self, client):
        self.client = client

    async def dispatch(self, event: str, data: dict = {}) -> typing.Tuple[list, dict]:
        """ Dispatches the parser and returns the args and kwargs"""
        coro = getattr(self, 'on_'+event.lower().replace('on_', ''), None)
        if callable(coro):
            return await coro(data)
        else:
            logger.warning(f"[EVENTS] Parser for event {event} was not found!")

    # Implementation of parsers that return args and kwargs for the event listeners

    async def on_message(self, data):
        buffer = self.client.message_broker.get_buffer('message')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_user_update(self, data):
        buffer = self.client.message_broker.get_buffer('user_update')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_house_join(self, data):
        buffer = self.client.message_broker.get_buffer('house_join')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_house_remove(self, data):
        buffer = self.client.message_broker.get_buffer('house_remove')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_house_update(self, data):
        buffer = self.client.message_broker.get_buffer('house_update')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_house_delete(self, data):
        buffer = self.client.message_broker.get_buffer('house_delete')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_house_downtime(self, data):
        buffer = self.client.message_broker.get_buffer('house_downtime')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_room_create(self, data):
        buffer = self.client.message_broker.get_buffer('room_create')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_room_update(self, data):
        buffer = self.client.message_broker.get_buffer('room_update')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_room_delete(self, data):
        buffer = self.client.message_broker.get_buffer('room_delete')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_house_member_join(self, data):
        buffer = self.client.message_broker.get_buffer('house_member_join')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_house_member_leave(self, data):
        buffer = self.client.message_broker.get_buffer('house_member_leave')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_house_member_enter(self, data):
        buffer = self.client.message_broker.get_buffer('house_member_enter')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_house_member_exit(self, data):
        buffer = self.client.message_broker.get_buffer('house_member_exit')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_member_update(self, data):
        buffer = self.client.message_broker.get_buffer('member_update')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_house_member_chunk(self, data):
        buffer = self.client.message_broker.get_buffer('house_member_chunk')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_batch_house_member_update(self, data):
        buffer = self.client.message_broker.get_buffer('batch_house_member_update')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_house_entity_update(self, data):
        buffer = self.client.message_broker.get_buffer('house_entity_update')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_relationship_update(self, data):
        buffer = self.client.message_broker.get_buffer('relationship_update')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_presence_update(self, data):
        buffer = self.client.message_broker.get_buffer('presence_update')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_message_create(self, data):
        buffer = self.client.message_broker.get_buffer('message_create')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_message_update(self, data):
        buffer = self.client.message_broker.get_buffer('message_update')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_message_delete(self, data):
        buffer = self.client.message_broker.get_buffer('message_delete')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)

    async def on_typing_start(self, data):
        buffer = self.client.message_broker.get_buffer('typing_start')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)