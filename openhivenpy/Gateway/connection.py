import asyncio
import sys

from openhivenpy.Types import Client
from openhivenpy.Events import EventHandler
from . import API, Websocket, HTTPClient

def ws_args(**kwargs):
    args = {
        "api_url": kwargs.get('api_url', "https://api.hiven.io"),
        "api_version": kwargs.get('api_version', "v1"),
        "token": kwargs.get('token', None),
        "heartbeat": kwargs.get('heartbeat', 30000),
        "ping_timeout": kwargs.get('ping_timeout', 100),
        "close_timeout": kwargs.get('close_timeout', 20),
        "ping_interval": kwargs.get('ping_interval', None),
        "event_loop": kwargs.get('event_loop')
    }
    return args

class Connection(Websocket, Client, API, HTTPClient):
    """`openhivenpy.Gateway.Connection` 
    
    HivenClient
    ~~~~~~~~~~~
    
    Class that wraps the Websocket, HTTPClient and the Data in the current connection to one class.
    
    Inherits from Websocket, Client, API and HTTPClient
    
    Parameter:
    ----------
    
    api_url: `str` - Url for the API which will be used to interact with Hiven. Defaults to 'https://api.hiven.io' 
    
    api_version: `str` - Version string for the API Version. Defaults to 'v1' 
    
    token: `str` - Needed for the authorization to Hiven. Will throw `HivenException.InvalidToken` if length not 128, is None or is empty
    
    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`
    
    ping_timeout: `int` - Seconds after the websocket will timeout after no succesful pong response. More information on the websockets documentation. Defaults to `100`
    
    close_timeout: `int` -  Seconds after the websocket will timeout after the end handshake didn't complete successfully. Defaults to `20`
    
    ping_interval: `int` - Interval for sending pings to the server. Defaults to `None` because else the websocket would timeout because the Hiven Websocket does not give a response
    
    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.
    
    """
    def __init__(self, event_handler: EventHandler, **kwargs):
        args = ws_args(**kwargs)
        super().__init__(event_handler=event_handler, **args)
        