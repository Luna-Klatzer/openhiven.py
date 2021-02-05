"""Exceptions used specifically for the module OpenHiven.py"""


__all__ = (
        'HivenException', 'HivenConnectionError', 'Forbidden',
        
        'Forbidden', 'InvalidClientType',
        'InvalidToken', 'UnableToClose', 'NoneClientType',

        'GatewayException',

        'WSFailedToHandle',

        'HTTPError', 'SessionCreateException', 'HTTPFaultyResponse',
        'HTTPFailedRequest', 'HTTPReceivedNoData',

        'FaultyInitialization', 'InvalidData',
        
        'CommandException')


class HivenException(Exception):
    """
    Base Exception in the openhivenpy library!
    
    All other exceptions inherit from this base class
    
    """
    def __init__(self, *args):
        if args:
            self.msg = "".join([str(arg) for arg in args])
        else:
            self.msg = f"{self.__name__}, Exception occurred in the package openhivenpy"
            
        super().__init__(self.msg)     
        
    def __str__(self):
        return self.msg

    def __call__(self):
        return self.__class__.__name__


class HivenConnectionError(HivenException):
    """
    The connection to Hiven failed to be kept alive or started!
    """
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = "The connection to Hiven failed to be kept alive or started!"
        super().__init__(arg)


class Forbidden(HivenException):
    """
    The client was forbidden to perform a Request
    """
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = "The client was forbidden to execute a certain task or function!"
        super().__init__(arg)


class FaultyInitialization(HivenException):
    """
    The object failed to initialise
    """
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = "The object failed to initialise"
        super().__init__(arg)


class InvalidData(FaultyInitialization):
    """
    Failed to utilise data as wanted due to missing or unexpected data!
    """

    def __init__(self, *args, data):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = "Failed to use data likely due to Faulty/Missing/Corrupt Data!"

        if data:
            arg += f"\n >> Data >> {data}"
        super().__init__(arg)


class InvalidClientType(HivenException):
    """
    Invalid client type was passed resulting in a failed initialisation!
    """
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = "Invalid client type was passed resulting in a failed initialization!"
        super().__init__(arg)


class InvalidToken(HivenException):
    """
    Invalid Token was passed!
    """
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = "Invalid Token was passed!"
        super().__init__(arg)


class GatewayException(HivenConnectionError):
    """
    General Exception in the Gateway and Connection to Hiven!
    """
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = "Gateway failed to !"
        super().__init__(arg)


class HTTPError(GatewayException):
    """
    Base Exception for exceptions in the HTTP and overall requesting
    """    
    def __init__(self, *args, code="Unknown"):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = f"Failed to perform request! Code: {code}! See HTTP logs!"
        super().__init__(arg) 


class HTTPFailedRequest(HTTPError):
    """
    General Exception for errors while handling a request
    """    
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = f"Failed to perform request! See HTTP logs!"
        super().__init__(arg) 


class HTTPFaultyResponse(HTTPError):
    """
    Response was in wrong format or expected data was not received
    """    
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = f"Unable to handle Response and use data! See HTTP logs!"
        super().__init__(arg)


class HTTPReceivedNoData(HTTPFaultyResponse):
    """
    Received a response without the required data field or
    received a 204(No Content) in a request that expected data.
    """
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = f"Received not the expected Data as response! See HTTP logs!"
        super().__init__(arg)


class SessionCreateException(HTTPError):
    """
    Failed to create Session!
    """    
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = f"Failed to create Session!"
        super().__init__(arg)


class UnableToClose(GatewayException):
    """
    The client is unable to close the connection to Hiven!
    """
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = "Failed to close Connection!"
        super().__init__(arg)


class WSFailedToHandle(GatewayException):
    """
    An Exception occurred while handling a message/response from Hiven
    """
    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = "Failed to handle WS Message!"
        super().__init__(arg)


class NoneClientType(Warning):
    """
    A None Type was passed in the Initialization!
    """    
    def __init__(self, *args):
        if args:
            msg = "".join([str(arg) for arg in args])
        else:
            msg = "A None ClientType was passed! This can indicate faulty usage of the Client and can cause errors!"
        super().__init__(msg)
        
# Command Exceptions #


class CommandException(HivenException):
    """
    General Exception while executing a command function on Hiven!
    """
    def __init__(self, *args):
        if args:
            arg = str(args[0]) + "".join([str(arg) for arg in args])
        else:
            arg = "An Exception occurred while executing a command function on Hiven!"
        super().__init__(arg)
