""" Openhiven.py related Exceptions """


__all__ = (
        'HivenException', 'ConnectionError', 'Forbidden', 
        
        'Forbidden', 'FaultyInitialization', 'InvalidClientType',
        'InvalidToken', 'UnableToClose', 'NoneClientType',
            
        'GatewayException', 'WSConnectionError', 'HTTPError',
        
        'CommandException')

class HivenException(Exception):
    """`openhivenpy.exception.HivenException`
    
    Base Exception in the openhivenpy library!
    
    All other exceptions inherit from this base class
    
    """
    def __init__(self, *args):
        if args:
            msg = "".join(arg for arg in args)
        else:
            msg = f"{self.__name__}, Exception occured in the package openhivenpy"
            
        super().__init__(msg)     
  
    @property
    def __name__(self):
        return "HivenException"   
  
class ConnectionError(HivenException):
    """`openhivenpy.exception.ConnectionError`
    
    The connection to Hiven failed to be kept alive or started!
    
    """
    def __init__(self, *args):
        if args:
            arg = "".join(arg for arg in args)
        else:
            arg = "The connection to Hiven failed to be kept alive or started!"
        super().__init__(arg)
        
    @property
    def __name__(self):
        return "ConnectionError"

class Forbidden(HivenException):
    """`openhivenpy.exception.Forbidden`

    The client was forbidden to execute a certain task or function
    
    """
    def __init__(self, *args):
        if args:
            arg = "".join(arg for arg in args)
        else:
            arg = "The client was forbidden to execute a certain task or function!"
        super().__init__(arg)
        
    @property
    def __name__(self):
        return "Forbidden"
    
class FaultyInitialization(HivenException):
    """`openhivenpy.exception.FaultyInitialization`
    
    The object was not initialized correctly and values were faulty passed or are entirely missing!
    
    """
    def __init__(self, *args):
        if args:
            arg = "".join(arg for arg in args)
        else:
            arg = "The object was not initialized correctly and values were faulty passed or are entirely missing!"
        super().__init__(arg)
    
class InvalidClientType(HivenException):
    """`openhivenpy.exception.InvalidClientType`
    
    Invalid client type was passed resulting in a failed initialization!
    
    """
    def __init__(self, *args):
        if args:
            arg = "".join(arg for arg in args)
        else:
            arg = "Invalid client type was passed resulting in a failed initialization!"
        super().__init__(arg)

class InvalidToken(HivenException):
    """`openhivenpy.exception.InvalidToken`
    
    Invalid Token was passed!
    
    """
    def __init__(self, *args):
        if args:
            arg = "".join(arg for arg in args)
        else:
            arg = "Invalid Token was passed!"
        super().__init__(arg)
        
class GatewayException(ConnectionError):
    """`openhivenpy.exception.GatewayException`
       
    General Exception in the Websocket!
    
    """    
    def __init__(self, *args):
        if args:
            arg = "".join(arg for arg in args)
        else:
            arg = "Exception occured in the running Websocket!"
        super().__init__(arg)

class HTTPError(ConnectionError):
    """`openhivenpy.exception.GatewayException`
       
    Base Exception for exceptions in the HTTPClient and overall requesting
    
    """    
    def __init__(self, code, *args):
        if args:
            arg = "".join(arg for arg in args)
        else:
            arg = f"Unable to process HTTP request! Code: {code}"
        super().__init__(arg) 

class UnableToClose(GatewayException):
    """`openhivenpy.exception.UnableToClose`
    
    The client is unable to close the connection to Hiven!
    
    """
    def __init__(self, *args):
        if args:
            arg = "".join(arg for arg in args)
        else:
            arg = "The client is unable to close the connection to Hiven!"
        super().__init__(arg)
        
class WSConnectionError(GatewayException):
    """`openhivenpy.exception.WSConnectionError`
    
    An Exception occured while trying to establish/keep the connection alive to Hiven!
    
    """
    def __init__(self, *args):
        if args:
            arg = "".join(arg for arg in args)
        else:
            arg = "The Websocket was unable to establish/keep the connection alive to Hiven!"
        super().__init__(arg)
        
class NoneClientType(Warning):
    """`openhivenpy.exception.NoneClientType`
    
    A None Type was passed in the Initialization!
    
    """    
    def __init__(self, *args):
        if args:
            msg = "".join(arg for arg in args)
        else:
            msg = "A None Type was passed in the Initialization!"
        super().__init__(msg)
        
# Command Exceptions #

class CommandException(HivenException):
    """`openhivenpy.exception.CommandException`
    
    General Exception while executing a command function on Hiven!
    
    """
    def __init__(self, *args):
        if args:
            arg = args[0] + "".join(arg for arg in args)
        else:
            arg = "An Exception occured while executing a command function on Hiven!"
        super().__init__(arg)
        