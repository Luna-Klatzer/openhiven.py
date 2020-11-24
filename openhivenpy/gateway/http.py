import aiohttp
import asyncio
import logging
import sys
import json as json_decoder
from typing import Optional

import openhivenpy.exceptions as errs

logger = logging.getLogger(__name__)

request_url_format = "{0}/{1}"

class HTTPClient():
    """`openhivenpy.gateway`
    
    HTTPClient
    ~~~~~~~~~~
    
    HTTPClient for requests and interaction with the Hiven API
    
    Parameter:
    ----------
    
    api_url: `str` - Url for the API which will be used to interact with Hiven. Defaults to 'https://api.hiven.io' 
    
    api_version: `str` - Version string for the API Version. Defaults to 'v1' 
    
    token: `str` - Needed for the authorization to Hiven.
    
    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.
    
    """
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(), **kwargs):
        
        self._TOKEN = kwargs.get('token')
        self.api_url = kwargs.get('api_url', "v1")
        self.api_version = kwargs.get('api_version', "https://api.hiven.io")
        self.request_url = request_url_format.format(self.api_url, self.api_version)        
        
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
            response = await self.raw_request("/users/@me", method="get")
            return await response.json()
        
        except Exception as e:
            self.http_ready = False
            await self.session.close()
            logger.error(f"Attempt to create session failed! Cause of Error: {e}")
            raise sys.exc_info()[-1](f"Attempt to create session failed! Cause of Error: {e}")  
            
    async def close(self) -> bool:
        """`openhivenpy.gateway.HTTPClient.connect()`

        Closes the connection to Hiven
        
        """
        try:
            await self.session.close()
            self.http_ready = False
        except Exception as e:
            logger.error(f"An error occured while trying to close the HTTP Connection to Hiven: {e}")
    
    async def raw_request(self, endpoint: str, *, method: str = "get", json_data: dict = None, timeout: int = 5, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.raw_request()`

        Wrapped HTTP request for a specified endpoint. 
        
        Returns the raw ClientResponse object
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json_data: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 5
        
        method: `str` - HTTP Method that should be used to perform the request
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        http_code = 400
        if self.http_ready:
            try:
                async with self.session.request(url=f"{self.request_url}{endpoint}", 
                                                headers=self.headers, 
                                                json=json_data, 
                                                timeout=timeout,
                                                method=method,
                                                **kwargs) as r:
                    http_code = r.status
                    
                    data = await r.read()
                    if r.status == 204:
                        error = True
                        error_code = "Empty Response"
                        error_message = "Got an empty response that cannot be converted to json!"
                    else:
                        json = json_decoder.loads(data)
                        
                        error = json.get('error', False)
                        if error:
                            error_code = json['error']['code'] if json['error'].get('code') != None else 'Unknown HTTP Error'
                            error_message = json['error']['message'] if json['error'].get('message') != None else 'Possibly faulty request or response!'
                        else:
                            error_code = 'Unknown HTTP Error'
                            error_message = 'Possibly faulty request or response!'

                    if r.status == 200 or r.status == 202:
                        if error == False:
                            return r
                        else:
                            logger.debug(f"Got HTTP Error Response with code {r.status} while performing HTTP '{method.upper()}' with endpoint: {self.request_url}{endpoint}; {error_code}, {error_message}")     
                            return None
                    else:
                        logger.debug(f"Got HTTP Error Response with code {r.status} while performing HTTP '{method.upper()}' with endpoint: {self.request_url}{endpoint}; {error_code}, {error_message}")
                        return None
    
            except Exception as e:
                logger.error(f"An error with code {http_code} occured while performing HTTP '{method.upper()}' with endpoint: {self.request_url}{endpoint}; {e}")
                raise errs.HTTPError(http_code, f"An error with code {http_code} occured while performing HTTP '{method.upper()}' with endpoint: {self.request_url}{endpoint}; {e}")
                    
        else:
            logger.error(f"The HTTPClient was not ready when trying to HTTP {method}! The connection is either faulty initalized or closed!")
            return None    
    
    async def request(self, endpoint: str, *, json_data: dict = None, timeout: int = 5, **kwargs) -> dict:
        """`openhivenpy.gateway.HTTPClient.request()`

        Wrapped HTTP request for a specified endpoint. 
        
        Returns a python dictionary containing the response data if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json_data: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 5
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        response = await self.raw_request(endpoint, method="get", timeout=timeout)
        if response != None:
            return await response.json()
        else:
            return None
    
    async def post(self, endpoint: str, *, json_data: dict = None, timeout: int = 5, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.post()`

        Wrapped HTTP Post for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json_data: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 5
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        return await self.raw_request(endpoint, json_data=json_data, timeout=timeout, method="post", **kwargs)
            
    async def delete(self, endpoint: str, *, timeout: int = 5, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.delete()`

        Wrapped HTTP delete for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json_data: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 5
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        
        """
        return await self.raw_request(endpoint, timeout=timeout, method="delete", **kwargs)
        
    async def put(self, endpoint: str, *, json_data: dict = None, timeout: int = 5, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.put()`

        Wrapped HTTP put for a specified endpoint.
        
        Similar to post, but multiple requests do not affect performance
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json_data: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 5
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        
        """
        return await self.raw_request(endpoint, json_data=json_data, timeout=timeout, method="put", **kwargs)
        
    async def patch(self, endpoint: str, *, json_data: dict = None, timeout: int = 5, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.patch()`

        Wrapped HTTP patch for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json_data: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 5
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        
        """
        return await self.raw_request(endpoint, json_data=json_data, timeout=timeout, method="patch", **kwargs)
    
    async def options(self, endpoint: str, *, json_data: dict = None, timeout: int = 5, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTPClient.options()`

        Wrapped HTTP options for a specified endpoint.
        
        Requests permission for performing communication with a URL or server
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json_data: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 5
        
        **kwargs: `any` - Other parameter for requesting. See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        return await self.raw_request(endpoint, json_data=json_data, timeout=timeout, method="options", **kwargs)
    