import asyncio
import logging

from ._get_type import getType
from openhivenpy.Gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class Presence:
    def __init__(self, data: dict, http_client: HTTPClient):
        self._http_client = http_client