""" Openhiven.py related Exceptions """


__all__ = (
        'HivenException', 'GatewayException', 'CommandException', 
        
        'Forbidden', 'FaultyInitialization', 'InvalidClientType',
        'InvalidToken', 
            
        'ConnectionError', 'WSConnectionError',
        
        'NoneClientType')

class HivenException(Exception):
    """`openhivenpy.exception.HivenException`
    
    Standard Exception in the openhivenpy library!
    
    """
    def __init__(self, *args):
        super().__init__(*args)
            
    def __str__(self):
        if self.message:
            return f"{self.__name__}, Exception occured in the package openhivenpy"
        else:
            return f"{self.__name__}, {self.message}"
        
class GatewayException(Exception):
    """`openhivenpy.exception.GatewayException`
       
    General Exception in the Websocket!
    
    """
    def __init__(self, *args):
        super().__init__(*args) 
        
    def __str__(self):
        if self.message:
            return f"{self.__name__}, Exception occured in the running Websocket"
        else:
            return f"{self.__name__}, {self.message}"

class Forbidden(Exception):
    """`openhivenpy.exception.Forbidden`

    The client was forbidden to execute a certain task or function
    
    """
    def __init__(self, *args):
        super().__init__(*args)
        
    def __str__(self):
        if self.message:
            return f"{self.__name__}, The client was forbidden to execute a certain task or function!"
        else:
            return f"{self.__name__}, {self.message}"

# Command Exceptions #

class CommandException(Exception):
    """`openhivenpy.exception.CommandException`
    
    General Exception while executing a command function on Hiven!
    
    """
    def __init__(self, *args):
        super().__init__(*args)
        
    def __str__(self):
        if self.message:
            return f"{self.__name__}, An Exception occured while executing a command function on Hiven!"
        else:
            return f"{self.__name__}, {self.message}"
    
class FaultyInitialization(HivenException):
    """`openhivenpy.exception.FaultyInitialization`
    
    The object was not initialized correctly and values were faulty passed or are entirely missing!
    
    """
    def __init__(self, *args):
        super().__init__(*args)
        
    def __str__(self):
        if self.message:
            return f"{self.__name__}, The object was not initialized correctly and values were faulty passed or are entirely missing!"
        else:
            return f"{self.__name__}, {self.message}"
    
class InvalidClientType(HivenException):
    """`openhivenpy.exception.InvalidClientType`
    
    Invalid client type was passed resulting in a failed initialization!
    
    """
    def __init__(self, *args):
        super().__init__(*args)
        
    def __str__(self):
        if self.message:
            return f"{self.__name__}, Invalid client type was passed resulting in a failed initialization!"
        else:
            return f"{self.__name__}, {self.message}"

class InvalidToken(HivenException):
    """`openhivenpy.exception.InvalidToken`
    
    Invalid Token was passed!
    
    """
    def __init__(self, *args):
        super().__init__(*args)
        
    def __str__(self):
        if self.message:
            return f"{self.__name__}, Invalid Token was passed!"
        else:
            return f"{self.__name__}, {self.message}"


class ConnectionError(GatewayException):
    """`openhivenpy.exception.ConnectionError`
    
    The connection to Hiven failed to be kept alive or started!
    
    """
    def __init__(self, *args):
        super().__init__(*args)
        
    def __str__(self):
        if self.message:
            return f"{self.__name__}, The connection to Hiven failed to be kept alive or started!"
        else:
            return f"{self.__name__}, {self.message}"

class WSConnectionError(ConnectionError):
    """`openhivenpy.exception.WSConnectionError`
    
    An Exception occured an error while trying to keep the connection alive to Hiven!
    
    """
    def __init__(self, *args):
        super().__init__(*args)
        
    def __str__(self):
        if self.message:
            return f"{self.__name__}, The Websocket or the HTTPClient was unable to connect to Hiven!!"
        else:
            return f"{self.__name__}, {self.message}"
        
class NoneClientType(Warning):
    """`openhivenpy.exception.NoneClientType`
    
    A None Type was passed in the Initialization!
    
    """    
    def __init__(self, *args):
        super().__init__(*args)
            
    def __str__(self):
        if self.message:
            return f"{self.__name__}, A None Type was passed in the Initialization!"
        else:
            return f"{self.__name__}, {self.message}"
        