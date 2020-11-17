import aiohttp
import asyncio
import logging
from typing import Optional

from openhivenpy.Exception import ConnectionError

logger = logging.getLogger(__name__)

request_url_format = "{0}/{1}"

class HTTPClient():
    """`openhivenpy.Gateway`
    
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
        
        self.loop = loop    
        
    async def connect(self) -> dict:
        """`openhivenpy.Gateway.HTTPClient.connect()`

        Establishes for the HTTPClient a connection to Hiven
        
        """
        try:
            self.session = aiohttp.ClientSession(loop=self.loop)
            
            async with self.session.get(url=f"{self.request_url}/users/@me", headers=self.headers) as r:
                if r.status == 200:
                    return await r.json()
                else:
                    raise ConnectionError(f"The Request to Hiven failed! Statuscode: {r.status}")
                
        except Exception as e:
            logger.error(f"An error occured while trying to request client data from Hiven: {e}")
            return None
            
    async def close(self) -> bool:
        """`openhivenpy.Gateway.HTTPClient.connect()`

        Closes the connection to Hiven
        
        """
        try:
            await self.session.close()
            self.http_ready = False
        except Exception as e:
            logger.error(f"An error occured while trying to close the HTTP Connection to Hiven: {e}")
    
    async def raw_request(self, endpoint: str, data: dict = None, timeout: int = 5) -> aiohttp.ClientResponse:
        """`openhivenpy.Gateway.HTTPClient.delete()`

        Wrapped HTTP request for a specified endpoint. 
        
        Returns the raw ClientResponse object
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        data: `str` - Version string for the API Version. Defaults to 'v1' 
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 5
        
        """
        if self.http_ready:
            async with self.session.request(method="get", url=f"{self.request_url}{endpoint}", 
                                           headers=self.headers, data=data) as r:
                if r.status == 200 or r.status == 202 or r.status == 204:
                    return r
                else:
                    logger.error(f"An error occured while performing HTTP request with endpoint: {self.request_url}{endpoint}")
                    return False
        else:
            logger.error("HTTPClient is not ready! The connection is either faulty initalized or closed!")
            return False    
    
    async def request(self, endpoint: str, data: dict = None, timeout: int = 5) -> dict:
        """`openhivenpy.Gateway.HTTPClient.delete()`

        Wrapped HTTP request for a specified endpoint. 
        
        Returns a python dictionary containing the response data if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        data: `str` - Version string for the API Version. Defaults to 'v1' 
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 5
        
        """
        if self.http_ready:
            async with self.session.request(method="get", url=f"{self.request_url}{endpoint}", 
                                           headers=self.headers, data=data) as r:
                if r.status == 200 or r.status == 202 or r.status == 204:
                    return await r.json()
                else:
                    logger.error(f"An error occured while performing HTTP request with endpoint: {self.request_url}{endpoint}")
                    return False
        else:
            logger.error("HTTPClient is not ready! The connection is either faulty initalized or closed!")
            return False    
    
    async def post(self, endpoint: str, data: dict = None) -> aiohttp.ClientResponse:
        """`openhivenpy.Gateway.HTTPClient.post()`

        Wrapped HTTP Post for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        data: `str` - Version string for the API Version. Defaults to 'v1' 
        
        """
        if self.http_ready:
            async with self.session.post(url=f"{self.request_url}{endpoint}", 
                                           headers=self.headers, json=data) as r:
                if r.status == 200 or r.status == 202 or r.status == 204:
                    return r
                else:
                    logger.error(f"An error occured while performing HTTP post with endpoint: {self.request_url}{endpoint}")
                    return None
        else:
            logger.error("HTTPClient is not ready! The connection is either faulty initalized or closed!")
            return None
            
    async def delete(self, endpoint: str) -> aiohttp.ClientResponse:
        """`openhivenpy.Gateway.HTTPClient.delete()`

        Wrapped HTTP delete for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        data: `str` - Version string for the API Version. Defaults to 'v1' 
        
        """
        if self.http_ready:
            async with self.session.delete(url=f"{self.request_url}{endpoint}", 
                                           headers=self.headers) as r:
                if r.status == 200 or r.status == 202 or r.status == 204:
                    return r
                else:
                    logger.error(f"An error occured while performing HTTP delete with endpoint: {self.request_url}{endpoint}")
                    return None
        else:
            logger.error("HTTPClient is not ready! The connection is either faulty initalized or closed!")
            return None
        
    async def put(self, endpoint: str, data: dict = None) -> aiohttp.ClientResponse:
        """`openhivenpy.Gateway.HTTPClient.put()`

        Wrapped HTTP put for a specified endpoint.
        
        Similar to post, but multiple requests do not affect performance
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        data: `str` - Version string for the API Version. Defaults to 'v1' 
        
        """
        if self.http_ready:
            async with self.session.put(url=f"{self.request_url}{endpoint}", 
                                           headers=self.headers, json=data) as r:
                if r.status == 200 or r.status == 202 or r.status == 204:
                    return r
                else:
                    logger.error(f"An error occured while performing HTTP put with endpoint: {self.request_url}{endpoint}")
                    return None
        else:
            logger.error("HTTPClient is not ready! The connection is either faulty initalized or closed!")
            return None
        
    async def patch(self, endpoint: str, data: dict = None) -> aiohttp.ClientResponse:
        """`openhivenpy.Gateway.HTTPClient.patch()`

        Wrapped HTTP patch for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        data: `str` - Version string for the API Version. Defaults to 'v1' 
        
        """
        if self.http_ready:
            async with self.session.patch(url=f"{self.request_url}{endpoint}", 
                                           headers=self.headers, json=data) as r:
                if r.status == 200 or r.status == 202 or r.status == 204:
                    return r
                else:
                    logger.error(f"An error occured while performing HTTP patch with endpoint: {self.request_url}{endpoint}")
                    return None
        else:
            logger.error("HTTPClient is not ready! The connection is either faulty initalized or closed!")
            return None
    
    async def options(self, endpoint: str, data: dict = None) -> aiohttp.ClientResponse:
        """`openhivenpy.Gateway.HTTPClient.options()`

        Wrapped HTTP options for a specified endpoint.
        
        Requests permission for performing communication with a URL or server
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..' Will be appended to the standard link: 'https://api.hiven.io/version'
    
        data: `str` - Version string for the API Version. Defaults to 'v1' 
        
        """
        if self.http_ready:
            async with self.session.options(url=f"{self.request_url}{endpoint}", 
                                           headers=self.headers, json=data) as r:
                if r.status == 200 or r.status == 202 or r.status == 204:
                    return r
                else:
                    logger.error(f"An error occured while performing HTTP options with endpoint: {self.request_url}{endpoint}")
                    return None
        else:
            logger.error("HTTPClient is not ready! The connection is either faulty initalized or closed!")
            return None    
    