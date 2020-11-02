# Hiven Exceptions #

class HivenException(Exception):
    """openhivenpy.Exception.HivenException
    
    Standard Exception in the openhivenpy library!
    
    """
    pass

class WebsocketException(Exception):
    """openhivenpy.Exception.WebsocketException
    
    General Exception in the Websocket!
    
    """
    pass
    
class InvalidClientType(HivenException):
    """openhivenpy.Exception.InvalidClientType
    
    Invalid Client type was passed and Initialization was not successful!
    
    """
    pass

class InvalidToken(HivenException):
    """openhivenpy.Exception.InvalidToken
    
    Invalid Token was passed!
    
    """
    pass

class NoneClientType(Warning):
    """openhivenpy.Exception.NoneClientType
    
    A None Type was passed in the Initialization!
    
    """
    pass

class UnableToConnect(WebsocketException):
    """openhivenpy.Exception.UnableToConnect
    
    The Websocket was unable to connect to the Hiven API. Possibly faulty Token!
    
    """
    pass

class WebsocketConnectionError(WebsocketException):
    """openhivenpy.Exception.WebsocketConnectionError
    
    An Exception occured an error while trying to keep a connection alive to Hiven!
    
    """
    pass

class FaultyInitializationError(Exception):
    """openhivenpy.Exception.FaultyInitializationError
    
    The objects were initialized correctly and values were not created or are entirely missing!
    
    """
    pass

# Command Exceptions #

class CommandException(Exception):
    """openhivenpy.Exception.CommandException
    
    General Exception while executing a command on Hiven!
    
    """
    pass #ToDo