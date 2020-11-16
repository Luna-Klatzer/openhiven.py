# Hiven Exceptions #

class HivenException(Exception):
    """`openhivenpy.Exception.HivenException`
    
    Standard Exception in the openhivenpy library!
    
    """
    pass

class GatewayException(Exception):
    """`openhivenpy.Exception.GatewayException`
       
    General Exception in the Websocket!
    
    """
    pass
    
class InvalidClientType(HivenException):
    """`openhivenpy.Exception.InvalidClientType`
    
    Invalid Client type was passed and Initialization was not successful!
    
    """
    pass

class InvalidToken(HivenException):
    """`openhivenpy.Exception.InvalidToken`
    
    Invalid Token was passed!
    
    """
    pass

class NoneClientType(Warning):
    """`openhivenpy.Exception.NoneClientType`
    
    A None Type was passed in the Initialization!
    
    """    
    pass


class ConnectionError(GatewayException):
    """`openhivenpy.Exception.UnableToConnect`
    
    The Websocket was unable to connect to the Hiven API. Possibly faulty Token!
    
    """
    pass

class WebsocketConnectionError(GatewayException):
    """`openhivenpy.Exception.WebsocketConnectionError`
    
    An Exception occured an error while trying to keep the connection alive to Hiven!
    
    """
    pass

class FaultyInitialization(Exception):
    """`openhivenpy.Exception.FaultyInitialization`
    
    The objects were initialized correctly and values were not created or are entirely missing!
    
    """
    pass

class Forbidden(Exception):
    """`openhivenpy.Exception.Forbidden`

    The client was forbidden to do a certain event
    
    """
    pass

# Command Exceptions #

class CommandException(Exception):
    """`openhivenpy.Exception.CommandException`
    
    General Exception while executing a command on Hiven!
    
    """
    pass #ToDo