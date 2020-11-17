import logging
import sys

import openhivenpy.Exception as errs
from openhivenpy.Gateway.http import HTTPClient
from ._get_type import getType

logger = logging.getLogger(__name__)

class Attatchment():
    def __init__(self, data: dict, http_client: HTTPClient):
        self._filename = data["filename"]
        self._mediaurl = data["media_url"]
        self._raw = data
        self._http_client = http_client

    @property
    def filename(self):
        return self._filename

    @property
    def media_url(self):
        return self._mediaurl
    
    @property
    def raw(self): #Different files have different attribs
        return self._raw
        