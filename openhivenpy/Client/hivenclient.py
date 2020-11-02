import asyncio
import requests
import sys
import warnings

from openhivenpy.Websocket import Websocket
from openhivenpy.Events import Events
import openhivenpy.Error.Exception as errs
from openhivenpy.Types import Client,ClientUser

API_URL = "https://api.hiven.io"
API_VERSION = "v1"

class HivenClient(Websocket, Events, Client):
    """openhivenpy.Client.HivenClient: Class HivenClient
    
    Main Class in openhivenpy and will be used to connect to the Hiven API and interact with it. Inherits from Websocket, Events and Client
    
    """
    def __init__(self, token: str, client_type: str = None,  heartbeat=30000, print_output=False, debug_mode=False):

        if client_type == "user" or client_type == "HivenClient.UserClient":
            self._CLIENT_TYPE = "HivenClient.UserClient"
            
        elif client_type == "bot" or client_type == "HivenClient.BotClient":
            self._CLIENT_TYPE = "HivenClient.BotClient"

        elif client_type == None:
            warnings.warn("Client type is None. Defaulting to BotClient. \nNote! This might be caused by using the HivenClient Class directly which leads to loss of some of the functions!", errs.NoneClientType)
            self._CLIENT_TYPE = "HivenClient.BotClient"

        else:
            raise errs.InvalidClientType(f"Expected 'user' or 'bot', got '{client_type}'") #Could use the diff lib here, and if that doesnt get anything then raise an error :thinking:
        

        if token == None or token == "":
            raise errs.InvalidToken("Token was not set")

        elif len(token) != 128:
            raise errs.InvalidToken("Invalid Token")

        self._CUSTOM_HEARBEAT = False if heartbeat == 30000 else True

        super().__init__(API_URL, API_VERSION, debug_mode, print_output, token, heartbeat)

        # Calling the function without any data so it's an empty object with setted attributes that are None at the moment
        self.update_client_data({})

    async def deactivate_print_output(self) -> None:
        """openhivenpy.Client.HivenClient.deactivate_print_output()
        
        Deactivates the output while listening to the Websocket of Hiven
        
        """
        try:
            self.PRINT_OUTPUT = False
            
        except AttributeError as e:
            raise errs.FaultyInitializationError(f"The attribute display_info_mode does not exist! The HivenClient Object was possibly not initialized correctly!\n{e}")

        except Exception as e:
            sys.stdout.write(str(e))
            
        return

    async def activate_print_output(self) -> None:
        """openhivenpy.Client.HivenClient.activate_print_output()
        
        Activates the output while listening to the Websocket of Hiven
        
        """
        try:
            self.PRINT_OUTPUT = True
            
        except AttributeError as e:
            raise errs.NoDisplayInfo(f"The attribute display_info_mode does not exist! The HivenClient Object was possibly not initialized correctly!\n{e}")

        except Exception as e:
            sys.stdout.write(str(e))
            
        return

    async def connect(self, token=None) -> None:
        """openhivenpy.Client.HivenClient.connect()
        
        Async function for establishing a connection to Hiven. Triggers HivenClient.on_connection_start(), HivenClient.on_init() and HivenClient.on_ready()
        
        """
        await self.create_connection()
        return 


    # Begin User Functions # 

    def run(self) -> None:
        """openhivenpy.Client.HivenClient.run()
        
        Standard function for establishing a connection to Hiven. Triggers on_connection_start(), on_init() and on_ready()
        
        """
        asyncio.run(self.start_event_loop())

    # End User Functions #
    # Begin User Properties #

    @property
    def user(self) -> ClientUser:
        return self._USERCLIENT

    @property
    def client_type(self) -> str:
        return self._CLIENT_TYPE

    @property
    def houses(self) -> list:
        return self._HOUSES

    @property
    def users(self) -> list:
        return self._USERS

        



