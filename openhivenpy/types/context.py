import logging

import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTP
from ._get_type import getType

logger = logging.getLogger(__name__)

__all__ = ['Context']


class Context:
    """`openhivenpy.types.Context` 
    
    Data Class for a Command or Event Context
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Returned with events, commands and HivenClient.on_ready()
    
    """
    def __init__(self, data: dict, http: HTTP):
        self._http = http