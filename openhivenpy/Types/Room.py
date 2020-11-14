import logging
import sys

from openhivenpy.Utils import utils
import openhivenpy.Exception as errs

logger = logging.getLogger(__name__)

class Room():
    """`openhivenpy.Types.Room`
    
    Data Class for a Hiven Room
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with house room lists and House.get_room()
    
    """
    def __init__(self, data: dict, auth_token: str): #These are all the attribs rooms have for now. Will add more when Phin says theyve been updated. Theres no functions. Yet.
        try:
            self._id = data.get('id')
            self._name = data.get('name')
            self._house = data.get("house_id")
            self._position = data.get("position")
            self._type = data.get("type") # 0 = Text, 1 = Portal
            self._emoji = data.get("emoji")
            self._description = data.get("description")
            self._AUTH_TOKEN = auth_token
            
        except AttributeError as e: 
            logger.error(e)
            raise errs.FaultyInitialization("The data of the object Room was not initialized correctly")
        
        except Exception as e: 
            logger.error(e)
            raise sys.exc_info()[0](e)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def house(self):
        return None #ToDo

    @property
    def position(self):
        return self._position
    
    @property
    def type(self):
        return self._type #ToDo: Other room classes.

    @property
    def emoji(self):
        return self._emoji.get("data") #Random type attrib there aswell
    
    @property
    def description(self):
        return self._description