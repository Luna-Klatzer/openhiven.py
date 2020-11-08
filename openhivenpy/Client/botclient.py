from .hivenclient import HivenClient

class BotClient(HivenClient):
    """`openhivenpy.Client.BotClient`
    
    BotClient
    ~~~~~~~~~
    
    Class for the specific use of a bot client on Hiven
    
    The class inherits all the attributes from HivenClient and will initialize with it
    
    """
    def __init__(self, token: str, heartbeat=30000):
        
        self._CLIENT_TYPE = "HivenClient.BotClient"
        super().__init__(token=token, client_type=self.client_type, heartbeat=heartbeat)

    def __repr__(self):
        return str(self._CLIENT_TYPE)

    def __str__(self):
        return str(self._CLIENT_TYPE)