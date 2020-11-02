from .hivenclient import HivenClient

class BotClient(HivenClient):
    """openhivenpy.Client.BotClient: HivenClient Class specific for a Bot Client
    
    The class inherits all the attributes from HivenClient and will initialize with it
    
    """
    def __init__(self, token: str, heartbeat=30000, debug_mode=False, print_output=False):
        
        self._CLIENT_TYPE = "HivenClient.BotClient"
        super().__init__(token=token, client_type=self.client_type, heartbeat=heartbeat, print_output=print_output, debug_mode=debug_mode)

    def __repr__(self):
        return str(self._CLIENT_TYPE)

    def __str__(self):
        return str(self._CLIENT_TYPE)