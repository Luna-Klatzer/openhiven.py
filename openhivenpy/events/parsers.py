import logging


__all__ = ['HivenParsers']

logger = logging.getLogger(__name__)


class HivenParsers:
    """ Event Parsers for Hiven Events that validate and update the cached data """
    def __init__(self, client):
        self.client = client

    async def dispatch(self, event: str, data):
        coro = getattr(self, event, None)
        if callable(coro):
            await coro(data)
        else:
            logger.warning(f"[EVENTS] Parser for event {event} was not found!")