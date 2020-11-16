import sys
import logging
import requests
import datetime

from .User import User

logger = logging.getLogger(__name__)

class Client():
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
            self._USER = User(data, self._TOKEN)
            return self

        except AttributeError as e: #Audible pain.
            logger.error(f"Error while updating information of the client: {e}")
            raise AttributeError("The data of the object User was not initialized correctly")
        except KeyError as e:
            pass
        except Exception as e:
            logger.error(f"Error while updating information of the client: {e}")
            raise sys.exc_info()[0](e)

    def __init__(self):
        self._HOUSES = [] #Python no likey appending to a read-only list
        self._USERS = []

    async def edit(self, data) -> bool:
        """`openhivenpy.ClientUser.edit`
        
        Change the signed in user's data. Available options: header, icon, bio, location, website.
        
        """
        if not type(data) == dir:
            raise SyntaxError(f"Expected dir, got {type(data)}")
        res = requests.patch("https://api.hiven.io/v1/users/@me", headers={"authorization": self._TOKEN,"User-Agent":"openhiven.py", "Content-Type":"application/json"},data=data)
        return res.status_code == 200
    
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
        return f"https://media.hiven.io/v1/users/{self._id}/icons/{self._icon}"

    @property
    def header(self) -> str:
        return f"https://media.hiven.io/v1/users/{self._id}/headers/{self._header}"
    
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
    def presence(self):
        return self._USER.presence

    @property
    def joined_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._joined_at) if self._joined_at != None else None