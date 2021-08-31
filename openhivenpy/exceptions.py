"""
Exceptions used specifically for the module openhiven.py

---

Under MIT License

Copyright © 2020 - 2021 Luna Klatzer

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
    'HivenError', 'HivenConnectionError', 'HivenENVError',

    'ClientTypeError', 'SessionCreateError', 'UnknownEventError',
    'InvalidTokenError', 'ClosingError', 'NoneClientType',

    'MessageBrokerError', 'EventConsumerLoopError', 'WorkerTaskError',

    'HivenGatewayError', 'KeepAliveError', 'WebSocketMessageError',
    'WebSocketFailedError', 'WebSocketClosedError', 'RestartSessionError',

    'HTTPError', 'HTTPSessionNotReadyError', 'HTTPRequestTimeoutError',
    'HTTPFailedRequestError', 'HTTPForbiddenError', 'HTTPResponseError',
    'HTTPReceivedNoDataError', 'HTTPNotFoundError', 'HTTPInternalServerError',
    'HTTPRateLimitError',

    'APIError',

    'InitializationError', 'InvalidPassedDataError',

    'ExecutionLoopError', 'ExecutionLoopStartError',

    'CommandError'
]


# -------- CORE --------


class HivenError(Exception):
    """
    Base Exception in the openhivenpy library!
    
    All other exceptions inherit from this base class
    """
    error_msg = None

    def __init__(self, *args):
        if self.error_msg is None or args:
            if args:
                self.error_msg = ", ".join([str(arg) for arg in args])
            else:
                self.error_msg = f"Exception occurred in the package openhivenpy"

        super().__init__(self.error_msg)

    def __str__(self):
        return self.error_msg


class HivenConnectionError(HivenError):
    """ The connection to Hiven failed to be kept alive or started! """
    error_msg = "The connection to Hiven failed to be kept alive or started!"


class HivenENVError(HivenError):
    """ The connection to Hiven failed to be kept alive or started! """
    error_msg = "Failed to load .env file of the module!"


class ClientTypeError(HivenError):
    """ Invalid client type was passed resulting in a failed initialisation! """
    error_msg = "Invalid client type was passed resulting in a failed initialization!"


class SessionCreateError(HivenConnectionError):
    """ Failed to create Session! """
    error_msg = "Failed to create Session!"


class UnknownEventError(HivenError):
    """ The attempt to register an event failed due to the specified event_listener not being found! """
    error_msg = "Failed to find event of the registered EventListener"


class InvalidTokenError(HivenError):
    """ Invalid Token was passed """
    error_msg = "Invalid Token was passed"


class ClosingError(HivenConnectionError):
    """ The client is unable to close the connection to Hiven! """
    error_msg = "Failed to close Connection!"


class NoneClientType(Warning):
    """ A None Type was passed in the Initialization! """
    error_msg = ("A None ClientType was passed! This can indicate faulty usage of the Client and could lead to errors"
                 "while running!")


# -------- MESSAGE BROKER --------


class MessageBrokerError(HivenError):
    """ An exception appeared in the message_broker, event_consumer or buffers """
    error_msg = "The message broker failed due to an exception"


class EventConsumerLoopError(MessageBrokerError):
    """ An exception appeared in the running event_consumer loop running the workers """
    error_msg = "The event_consumer failed to run properly due to an exception occurring"


class WorkerTaskError(EventConsumerLoopError):
    """ An exception occurred in the running worker process """
    error_msg = "The worker failed to execute properly due to an exception occurring"


# -------- GATEWAY --------


class HivenGatewayError(HivenConnectionError):
    """ General Exception in the Gateway and Connection to Hiven! """
    error_msg = "Encountered an Exception in the Hiven Gateway!"


class KeepAliveError(HivenConnectionError):
    """ General Exception in the KeepAlive process loop """
    error_msg = "Failed to process KeepAlive due to an exception occurring"


# -------- WEBSOCKET --------

class WebSocketMessageError(HivenGatewayError):
    """ An Exception occurred while handling a message/response from Hiven """
    error_msg = "Failed to handle WebSocket Message!"


class WebSocketFailedError(HivenGatewayError):
    """ Received an exception call  """
    error_msg = "Received Error frame from the aiohttp Websocket which resulted in the crashing of the WebSocket!"


class WebSocketClosedError(HivenError):
    """ The Hiven WebSocket was closed and an exception is raised to stop the current processes """
    error_msg = "The Hiven WebSocket is closing!"


class RestartSessionError(HivenGatewayError):
    """ Exception used to trigger restarts in the gateway module """
    error_msg = "Restarting the Session and re-initialising the data!"


# -------- HTTP --------


class HTTPError(HivenGatewayError):
    """ Base Exception for exceptions in the HTTP and overall requesting """
    error_msg = "Failed to perform request! Code: {}! See HTTP logs!"

    def __init__(self, *args, code="Unknown"):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = self.error_msg.format(code)
        super().__init__(arg)


class HTTPRequestTimeoutError(HTTPError):
    """ The sent request did not finish in time and raised a timeout exception """
    error_msg = "Failed to perform request in time!"

    def __init__(self, *args):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = self.error_msg
        super().__init__(arg)


class HTTPFailedRequestError(HTTPError):
    """ General Exception for errors while handling a request """
    error_msg = "Failed to perform a request"


class HTTPNotFoundError(HTTPError):
    """ Failed to reach the specified endpoint """
    error_msg = "Failed to reach the specified endpoint [Code: 404]"


class HTTPRateLimitError(HTTPError):
    """ Received a RateLimit which blocks the request from performing """
    error_msg = "Failed to reach the specified endpoint due to rate-limit " \
                "[Code: 429]"


class HTTPInternalServerError(HTTPError):
    """ Failed to reach the specified endpoint """
    error_msg = "Failed to perform request due to Hiven internal server " \
                "error [Code: 5**]"


class HTTPSessionNotReadyError(HTTPError):
    """ The HTTP Session is not initialised yet """
    error_msg = "HTTP-Client not initialised"


class HTTPForbiddenError(HTTPFailedRequestError):
    """ The client was forbidden to perform a Request """
    error_msg = "The client was forbidden to execute a certain task or " \
                "function!"


class HTTPResponseError(HTTPError):
    """ Response was in wrong format or expected data was not received """
    error_msg = "Failed to handle Response and utilise data! Code: {}! " \
                "See HTTP logs!"


class HTTPReceivedNoDataError(HTTPError):
    """
    Received a response without the required data field or
    received a 204(No Content) in a request that expected data.
    """
    error_msg = "Response does not contain the expected Data! Code: {}! " \
                "See HTTP logs!"


# -------- API --------


class APIError(HTTPError):
    """
    An exception in an API-related function that was unable to properly
    interact with the Hiven servers
    """
    error_msg = "Failed to properly execute the API function"


class APIForbidden(APIError):
    """
    An exception in an API-related function that was unable to properly
    interact with the Hiven servers
    """
    error_msg = "You do not have the permission to perform this action"


# -------- DATA --------

class InitializationError(HivenError):
    """ The object failed to initialise """
    error_msg = "The object failed to initialise"


class InvalidPassedDataError(InitializationError):
    """ Failed to utilise data as wanted due to missing or unexpected data! """

    def __init__(self, *args, data):
        if args:
            arg = "".join([str(arg) for arg in args])
        else:
            arg = "The initializer failed to validate and utilise the data " \
                  "likely due to wrong data passed!"

        if data:
            arg += f"\n Data: {data}"
        super().__init__(arg)


# -------- ExecutionLoop --------


class ExecutionLoopError(HivenError):
    """
    An exception occurred in the execution loop running parallel to the core
    """
    error_msg = "An exception occurred in the execution loop running parallel " \
                "to the core"


class ExecutionLoopStartError(HivenError):
    """ The execution failed to start and crashed """
    error_msg = "Failed to start the Execution Loop"


# -------- COMMAND --------


class CommandError(HivenError):
    """ General Exception while executing a command function on Hiven! """
    error_msg = "An Exception occurred while executing a command on Hiven!"
