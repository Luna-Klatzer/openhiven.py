from .Message import Message

class Context():
    """`openhivenpy.Types.House` 
    
    Data Class for a Command or Event Context
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with events, commands and HivenClient.on_ready()
    
    """
    def __init__(self, data: dict):
        pass