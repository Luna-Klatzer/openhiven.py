"""
Exceptions used specifically for the module OpenHiven.py

---

Under MIT License

Copyright © 2020 Frostbyte Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


__all__ = [
    'HivenError', 'HivenConnectionError', 'HTTPForbiddenError',

    'HTTPForbiddenError', 'ClientTypeError',
    'InvalidTokenError', 'ClosingError', 'NoneClientType',

    'HivenGatewayError', 'WebSocketClosedError', 'RestartSessionError',

    'WebSocketMessageError',

    'HTTPError', 'SessionCreateError', 'HTTPResponseError',
    'HTTPFailedRequestError', 'HTTPReceivedNoDataError',

    'InitializationError', 'InvalidPassedDataError', 'ExpectedAsyncFunction',

    'CommandError'
]


class HivenError(Exception):
    """
    Base Exception in the openhivenpy library!
    
    All other exceptions inherit from this base class
    """
    exc_msg = None

    def __init__(self, *args):
        if self.exc_msg is None or args:
            if args:
                self.exc_msg = ", ".join([str(arg) for arg in args])
            else:
                self.exc_msg = f"Exception occurred in the package openhivenpy"

        super().__init__(self.exc_msg)
        
    def __str__(self):
        return self.exc_msg

    def __repr__(self):
        return "<{} exc_msg={}>".format(self.__class__.__name__, self.exc_msg)

    def __call__(self):
        return str(self)


class HivenConnectionError(HivenError):
    """ The connection to Hiven failed to be kept alive or started! """
    exc_msg = "The connection to Hiven failed to be kept alive or started!"


class HTTPForbiddenError(HivenError):
    """ The client was forbidden to perform a Request """
    exc_msg = "The client was forbidden to execute a certain task or function!"


class InitializationError(HivenError):
    """ The object failed to initialise """
    exc_msg = "The object failed to initialise"


class InvalidPassedDataError(InitializationError):
    """ Failed to utilise data as wanted due to missing or unexpected data! """
    def __init__(self, *args, data):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = "The initializer failed to validate and utilise the data likely due to wrong data passed!"

        if data:
            arg += f"\n Data: {data}"
        super().__init__(arg)


class ClientTypeError(HivenError):
    """ Invalid client type was passed resulting in a failed initialisation! """
    exc_msg = "Invalid client type was passed resulting in a failed initialization!"


class ExpectedAsyncFunction(HivenError):
    """ The passed function of the decorator is not async and cannot be used """
    exc_msg = "The passed function is not async"


class InvalidTokenError(HivenError):
    """ Invalid Token was passed! """
    exc_msg = "Invalid Token was passed!"


class HivenGatewayError(HivenConnectionError):
    """ General Exception in the Gateway and Connection to Hiven! """
    exc_msg = "Encountered and Exception in the Hiven Gateway!"


class WebSocketClosedError(HivenError):
    """ The Hiven WebSocket was closed and an exception is raised to stop the current processes """
    exc_msg = "The Hiven WebSocket is closing!"


class RestartSessionError(HivenGatewayError):
    """ Exception used to trigger restarts in the gateway module """
    exc_msg = "Restarting the Session and re-initialising the data!"


class HTTPError(HivenGatewayError):
    """ Base Exception for exceptions in the HTTP and overall requesting """
    exc_msg = "Failed to perform request! Code: {}! See HTTP logs!"

    def __init__(self, *args, code="Unknown"):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = self.exc_msg.format(code)
        super().__init__(arg) 


class HTTPFailedRequestError(HTTPError):
    """ General Exception for errors while handling a request """


class HTTPResponseError(HTTPError):
    """ Response was in wrong format or expected data was not received """
    exc_msg = "Failed to handle Response and utilise data! Code: {}! See HTTP logs!"


class HTTPReceivedNoDataError(HTTPError):
    """
    Received a response without the required data field or
    received a 204(No Content) in a request that expected data.
    """
    exc_msg = "Response does not contain the expected Data! Code: {}! See HTTP logs!"


class SessionCreateError(HivenError):
    """ Failed to create Session! """
    exc_msg = "Failed to create Session!"


class ClosingError(HivenGatewayError):
    """ The client is unable to close the connection to Hiven! """
    exc_msg = "Failed to close Connection!"


class WebSocketMessageError(HivenGatewayError):
    """ An Exception occurred while handling a message/response from Hiven """
    exc_msg = "Failed to handle WebSocket Message!"


class NoneClientType(Warning):
    """ A None Type was passed in the Initialization! """
    exc_msg = ("A None ClientType was passed! This can indicate faulty usage of the Client and could lead to errors"
               "while running!")
        
# Command Exceptions #


class CommandError(HivenError):
    """ General Exception while executing a command function on Hiven! """
    exc_msg = "An Exception occurred while executing a command on Hiven!"
