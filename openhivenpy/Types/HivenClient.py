import sys
import logging
import requests
import datetime

from ._get_type import getType

logger = logging.getLogger(__name__)

class HivenClient():
    """`openhivenpy.Types.HivenClient` 
    
    Date Class for a HivenClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Data Class that stores the data of the connected Client
    
    """
    async def update_client_data(self, data: dict) -> None:
        """`openhivenpy.Types.Client.update_client_data()`
         
        Updates or creates the standard user data attributes of the HivenClient
        
        """
        try: 
            # Using a USER object to actually store all user data
            self._USER = await getType.a_User(data, self.http_client)
            
        except AttributeError as e: #Audible pain.
            logger.error(f"Error while updating information of the client: {e}")
            raise AttributeError("The data of the object User was not initialized correctly")
        except KeyError as e:
            pass
        except Exception as e:
            logger.error(f"Error while updating information of the client: {e}")
            raise sys.exc_info()[0](e)

    def __init__(self):
        self._houses = [] #Python no likey appending to a read-only list
        self._users = []
        self._rooms = []

    async def edit(self, data: str, value: str) -> bool:
        """`openhivenpy.ClientUser.edit()`
        
        Change the signed in user's/bot's data. 
        
        Available options: header, icon, bio, location, website.
        
        Returns `True` if successful
        
        """
        execution_code = None
        try:
            if data in ['header', 'icon', 'bio', 'location', 'website']:
                response = await self.http_client.patch(endpoint="/users/@me", data={data: value})
                execution_code = response.status
                return True
            else:
                logger.error("The passed value does not exist in the user context!")
                raise KeyError("The passed value does not exist in the user context!")
    
        except Exception as e:
            logger.critical(f"Error while trying to change the value {data} on the Client Account. [CODE={execution_code}] {e}")
            raise sys.exc_info()[0](e)    

    @property
    def username(self) -> str:
        return self._USER.username

    @property
    def name(self) -> str:
        return self._USER.name

    @property
    def id(self) -> int:
        return self._USER.id

    @property
    def icon(self) -> str:
        return self._USER._icon
    
    @property
    def header(self) -> str:
        return self._USER._header

    @property
    def bot(self) -> bool:
        return self._USER.bot

    @property
    def location(self) -> str:
        return self._USER.location

    @property
    def website(self) -> str:
        return self._USER.website

    @property
    def presence(self) -> getType.Presence:
        return self._USER.presence

    @property
    def joined_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._USER._joined_at) if self._USER._joined_at != None else None