import sys
import logging
from .User import User
from .ClientUser import ClientUser

logger = logging.getLogger(__name__)

class Client(): #Why inherit User?
    """`openhivenpy.Types.Client` 
    
    Data Class for HivenClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Used for the general data in the HivenClient and inherits all the avaible data from Hiven(attr -> readonly)!
    
    Returned as HivenClient(or specified Client Type) in on_init() and with UserClient(), BotClient() and HivenClient()
    
    """
    def update_client_data(self, data: dict) -> None:
        """
        Updates or creates the standard data of the HivenClient
        
        Returns if the Client class inherited the caller class and else the Client Class itself
        
        """
        try: 
            self._HOUSES = [] #Python no likey appending to a read-only list
            self._USERS = []
            self._USERCLIENT = ClientUser(data,self._TOKEN)
            return self

        except AttributeError: #Audible pain.
            logger.error(e)
            raise AttributeError("The data of the object User was not initialized correctly")
        except KeyError as e:
            pass
        except Exception as e:
            logger.error(e)
            raise sys.exc_info()[0](e)

    def __init__(self,data,token):
        self.update_client_data(data)