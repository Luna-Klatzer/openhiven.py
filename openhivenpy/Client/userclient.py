from .hivenclient import HivenClient

class UserClient(HivenClient):
    """`openhivenpy.Client.UserClient`
    
    UserClient
    ~~~~~~~~~~
    
    Class for the specific use of a user client on Hiven
    
    The class inherits all the attributes from HivenClient and will initialize with it
    
    """
    def __init__(self, token: str, heartbeat=30000):

        self._CLIENT_TYPE = "HivenClient.UserClient"
        super().__init__(token=token, client_type=self.client_type, heartbeat=heartbeat)

    def __repr__(self) -> str:
        return str(self._CLIENT_TYPE)

    def __str__(self) -> str:
        return str(self._CLIENT_TYPE)

        