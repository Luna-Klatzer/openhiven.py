import logging
import typing

__all__ = ['HivenParsers']

logger = logging.getLogger(__name__)


class HivenParsers:
    """ Event Parsers for Hiven Events that validate and update the cached data """
    def __init__(self, client):
        self.client = client

    async def dispatch(self, event: str, data) -> typing.Tuple[list, dict]:
        """ Dispatches the parser and returns the args and kwargs"""
        coro = getattr(self, 'on_'+event.lower().replace('on_', ''), None)
        if callable(coro):
            return await coro(data)
        else:
            logger.warning(f"[EVENTS] Parser for event {event} was not found!")

    # Implementation of parsers that return args and kwargs

    async def on_message(self, data):
        buffer = self.client.message_broker.get_buffer('message')
        # Parsing that is required in the future
        args = []
        kwargs = {}
        buffer.add(data, *args, **kwargs)
