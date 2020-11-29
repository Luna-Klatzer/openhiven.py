import aiohttp
import asyncio
import logging
import sys
import time
import json as json_decoder
from typing import Optional

import openhivenpy.exceptions as errs

__all__ = ('HTTPClient')


logger = logging.getLogger(__name__)

request_url_format = "{0}/{1}"

class HTTPClient():
    """`openhivenpy.gateway`
    
    HTTPClient
    ~~~~~~~~~~
    
    HTTPClient for requests and interaction with the Hiven API
    
    Parameter:
    ----------
    
    api_url: `str` - Url for the API which will be used to interact with Hiven. Defaults to 'https://api.hiven.io/v1' 
    
    host: `str` - Host URL. Defaults to "https://api.hiven.io"
    
    api_version: `str` - Version string for the API Version. Defaults to 'v1' 
    
    token: `str` - Needed for the authorization to Hiven.
    
    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.
    
    """
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(), **kwargs):
        
        self._TOKEN = kwargs.get('token')
        self.host = kwargs.get('api_url', "v1")
        self.api_version = kwargs.get('api_version', "https://api.hiven.io")
        self.api_url = request_url_format.format(self.host, self.api_version)        
        
        self.headers = {"Content-Type": "application/json", 
                        "User-Agent":"openhiven.py by ©FrostbyteSpace on GitHub",
                        "Authorization": self._TOKEN}
        
        self.http_ready = False
        
        self.session = None
        self.loop = loop    
        
    async def connect(self) -> dict:
        """`openhivenpy.gateway.HTTPClient.connect()`

        Establishes for the HTTPClient a connection to Hiven
        
        """
        try:
            self.session = aiohttp.ClientSession(loop=self.loop)
            self.http_ready = True
            response = await self.request("/users/@me", timeout=10)
            return response
        
        except Exception as e:
            self.http_ready = False
            await self.session.close()
            logger.error(f"Attempt to create session failed! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToCreateSession(f"Attempt to create session failed! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")  
            
    async def close(self) -> bool:
        """`openhivenpy.gateway.HTTPClient.connect()`

        Closes the HTTP session that is currently connected to Hiven!
        
        """
        try:
            await self.session.close()
            self.http_ready = False
        except Exception as e:
            logger.error(f"An error occured while trying to close the HTTP Connection to Hiven: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.HTTPError(f"Attempt to create session failed! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")  
    
    async def raw_request(self, endpoint: str, *, method: str = "GET", json: dict = None, timeout: float = 15, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.raw_request()`

        Wrapped HTTP request for a specified endpoint. 
        
        Returns the raw ClientResponse object
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15
        
        method: `str` - HTTP Method that should be used to perform the request
        
        headers: `dict` - Defaults to the normal headers
                
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        # Timeout Handler that watches if the request takes too long
        async def _time_out_handler(timeout: float) -> None:
            start_time = time.time()
            timeout_limit = start_time + timeout
            while True:
                if self._request.done():
                    break
                elif time.time() > timeout_limit:
                    if not self._request.cancelled():
                        self._request.cancel()
                    logger.debug(f"[{self.host}] HTTP '{method.upper()}' failed with endpoint: "
                                 f"{endpoint}; Request to Hiven timed out!")
                    break
                await asyncio.sleep(0.25)
            return None

        async def _request(endpoint, method, json, **kwargs):
            http_code = "Unknown Internal Error"
            # Deactivated because of errors that occured using it!
            timeout = aiohttp.ClientTimeout(total=None)
            if self.http_ready:
                try:
                    if kwargs.get('headers') == None:
                        headers = self.headers
                    else:
                        headers = kwargs.pop('headers')
                    url = f"{self.api_url}{endpoint}"
                    async with self.session.request(
                                                    method=method,
                                                    url=url,
                                                    headers=headers, 
                                                    json=json,
                                                    timeout=timeout,
                                                    **kwargs) as resp:
                        http_code = resp.status
                        
                        if resp.status < 300:
                            data = await resp.read()
                            if resp.status == 204:
                                error = True
                                error_code = "Empty Response"
                                error_reason = "Got an empty response that cannot be converted to json!"
                            else:
                                json = json_decoder.loads(data)
                                
                                error = json.get('error', False)
                                if error:
                                    error_code = json['error']['code'] if json['error'].get('code') != None else 'Unknown HTTP Error'
                                    error_reason = json['error']['message'] if json['error'].get('message') != None else 'Possibly faulty request or response!'
                                else:
                                    error_code = 'Unknown HTTP Error'
                                    error_reason = 'Possibly faulty request or response!'

                            if resp.status == 200 or resp.status == 202:
                                if error == False:
                                    return resp
                                
                        error_code = resp.status
                        error_reason = resp.reason

                        logger.debug(f"[{self.host}] HTTP '{method.upper()}' failed with endpoint: " 
                                     f"{endpoint}; {error_code}, {error_reason}")
                        return resp
        
                except asyncio.TimeoutError as e:
                    logger.error(f"[{self.host}] HTTP '{method.upper()}' failed with endpoint: {endpoint}; Request to Hiven timed out!")
                    raise errs.HTTPError(http_code, f"An error with code {http_code} occured while performing HTTP " 
                                         f"'{method.upper()}' with endpoint: {self.host}{endpoint}; Request to Hiven timed out!")

                except Exception as e:
                    logger.error(f"[{self.host}] HTTP '{method.upper()}' failed with endpoint: {endpoint}; {sys.exc_info()[1].__class__.__name__}, {str(e)}")
                    raise errs.HTTPError(http_code, f"An error with code {http_code} occured while performing HTTP '{method.upper()}' with endpoint: {self.host}{endpoint}; {sys.exc_info()[1].__class__.__name__}, {str(e)}")
                        
            else:
                logger.error(f"The HTTPClient was not ready when trying to HTTP {method}!" 
                             "The connection is either faulty initalized or closed!")
                return None    

        self._request = self.loop.create_task(_request(endpoint, method, json, **kwargs))
        _task_time_out_handler = self.loop.create_task(_time_out_handler(timeout))

        try:
            resp = await asyncio.gather(self._request, _task_time_out_handler)
        except asyncio.CancelledError:
            logger.debug(f"Request was cancelled!")
            return
        except Exception as e:
            logger.error(f"An error occured while performing HTTP '{method.upper()}' with endpoint: {self.host}{endpoint}; {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.HTTPError(f"An error occured while performing HTTP '{method.upper()}' with endpoint: {self.host}{endpoint}; {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        return resp[0]
    
    async def request(self, endpoint: str, *, json: dict = None, timeout: float = 15, **kwargs) -> dict:
        """`openhivenpy.gateway.HTTPClient.request()`

        Wrapped HTTP request for a specified endpoint. 
        
        Returns a python dictionary containing the response data if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15
        
        headers: `dict` - Defaults to the normal headers
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        response = await self.raw_request(endpoint, method="GET", timeout=timeout, **kwargs)
        if response != None:
            return await response.json()
        else:
            return None
    
    async def post(self, endpoint: str, *, json: dict = None, timeout: float = 15, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.post()`

        Wrapped HTTP Post for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15
        
        headers: `dict` - Defaults to the normal headers
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        return await self.raw_request(endpoint, method="POST", json=json, timeout=timeout, **kwargs)
            
    async def delete(self, endpoint: str, *, timeout: int = 10, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.delete()`

        Wrapped HTTP delete for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15
        
        headers: `dict` - Defaults to the normal headers
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info

        """
        return await self.raw_request(endpoint, method="DELETE", timeout=timeout, **kwargs)
        
    async def put(self, endpoint: str, *, json: dict = None, timeout: float = 15, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.put()`

        Wrapped HTTP put for a specified endpoint.
        
        Similar to post, but multiple requests do not affect performance
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15
        
        headers: `dict` - Defaults to the normal headers
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info

        """
        return await self.raw_request(endpoint, method="PUT", json=json, timeout=timeout, **kwargs)
        
    async def patch(self, endpoint: str, *, json: dict = None, timeout: float = 15, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.patch()`

        Wrapped HTTP patch for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15
        
        headers: `dict` - Defaults to the normal headers
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info

        """
        return await self.raw_request(endpoint, method="PATCH", json=json, timeout=timeout, **kwargs)
    
    async def options(self, endpoint: str, *, json: dict = None, timeout: float = 15, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.options()`

        Wrapped HTTP options for a specified endpoint.
        
        Requests permission for performing communication with a URL or server
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15
        
        headers: `dict` - Defaults to the normal headers
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        return await self.raw_request(endpoint, method="OPTIONS", json=json, timeout=timeout, **kwargs)
    