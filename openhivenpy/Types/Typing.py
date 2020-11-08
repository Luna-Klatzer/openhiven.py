import datetime

from openhivenpy.Types import *
import openhivenpy.Utils as utils 

class Typing():
    """`openhivenpy.Types.Typing`
    
    Data Class for Typing
    ~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with HivenClient.on_typing_start() and HivenClient.on_typing_end()
    
    """
    def __init__(self, data: dict):
        self._MEMBER = data['author_id']
        self._HOUSE = data['house_id']
        self._ROOM = data['room_id']
        self._TIMESTAMP = data['timestamp']

    @property
    def timestamp(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self._TIMESTAMP)