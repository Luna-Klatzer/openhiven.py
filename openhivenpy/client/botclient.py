import asyncio
import logging
from typing import Optional

from .hivenclient import HivenClient

__all__ = ['BotClient']

logger = logging.getLogger(__name__)


class BotClient(HivenClient):
    """ Class for the specific use of a bot Application on Hiven """
    pass
