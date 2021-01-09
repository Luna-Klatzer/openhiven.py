import aiohttp
import asyncio
import logging
import sys
import time
import json as json_decoder
from typing import Optional, Union

import openhivenpy.exceptions as errs

__all__ = 'HTTP'

logger = logging.getLogger(__name__)

request_url_format = "https://{0}/{1}"


class HTTP:
    """`openhivenpy.gateway`
    
    HTTP
    ~~~~~~~~~~
    
    HTTP-Client for requests and interaction with the Hiven API
    
    Parameter:
    ----------
    
    api_url: `str` - Url for the API which will be used to interact with Hiven. Defaults to 'https://api.hiven.io/v1' 
    
    host: `str` - Host URL. Defaults to "api.hiven.io"
    
    api_version: `str` - Version string for the API Version. Defaults to 'v1' 
    
    token: `str` - Needed for the authorization to Hiven.
    
    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.
    
    """
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(), **kwargs):
        
        self._TOKEN = kwargs.get('token')
        self.host = kwargs.get('api_url', "api.hiven.io")
        self.api_version = kwargs.get('api_version', "v1")
        self.api_url = request_url_format.format(self.host, self.api_version)        
        
        self.headers = {"Authorization": self._TOKEN,
                        "Host": self.host}
        
        self._ready = False
        
        self.session = None
        self.loop = loop

        # Last/Currently executed request
        self._request = None

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('ready', self.ready),
            ('host', self.host),
            ('api_version', self.api_version),
            ('headers', self.headers)
        ]
        return '<HTTP {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def ready(self):
        return self._ready

    async def connect(self) -> Union[aiohttp.ClientSession, None]:
        """`openhivenpy.gateway.HTTP.connect()`

        Establishes for the HTTP a connection to Hiven
        
        """
        try:
            async def on_request_start(session, trace_config_ctx, params):
                logger.debug(f"[HTTP] >> Request with HTTP {params.method} started at {time.time()}")
                logger.debug(f"[HTTP] >> URL >> {params.url}")
         
            async def on_request_end(session, trace_config_ctx, params):
                logger.debug(f"[HTTP] << Request with HTTP {params.method} finished!")
                logger.debug(f"[HTTP] << Header << {params.headers}")
                logger.debug(f"[HTTP] << URL << {params.url}")
                logger.debug(f"[HTTP] << Response << {params.response}")
            
            async def on_request_exception(session, trace_config_ctx, params):
                logger.debug(f"[HTTP] << An exception occurred while executing the request")
            
            async def on_request_redirect(session, trace_config_ctx, params):
                logger.debug(f"[HTTP] << REDIRECTING with URL {params.url} and HTTP {params.method}")

            async def on_response_chunk_received(session, trace_config_ctx, params):
                logger.debug(f"[HTTP] << Chunk Received << {params.chunk}\n")

            async def on_connection_queued_start(session, trace_config_ctx, params):
                logger.debug(f"[HTTP] >> HTTP {params.method} with {params.url} queued!")
            
            trace_config = aiohttp.TraceConfig()
            trace_config.on_request_start.append(on_request_start)
            trace_config.on_request_end.append(on_request_end)
            trace_config.on_request_exception.append(on_request_exception)
            trace_config.on_request_redirect.append(on_request_redirect)
            trace_config.on_connection_queued_start.append(on_connection_queued_start)
            trace_config.on_response_chunk_received.append(on_response_chunk_received)
            
            self.session = aiohttp.ClientSession(loop=self.loop, trace_configs=[trace_config])
            self._ready = True
            resp = await self.request("/users/@me", timeout=10)
            if resp:
                return self.session
            else:
                return None
        
        except Exception as e:
            self._ready = False
            await self.session.close()
            logger.error(f"[HTTP] FAILED to create Session! > {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToCreateSession(f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")

    async def close(self) -> bool:
        """`openhivenpy.gateway.HTTP.connect()`

        Closes the HTTP session that is currently connected to Hiven!
        
        """
        try:
            await self.session.close()
            self._ready = False
            return True
        except Exception as e:
            logger.error(f"[HTTP] Failed to close HTTP Session: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.HTTPError(f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")
    
    async def raw_request(
                        self, 
                        endpoint: str, 
                        *, 
                        method: str = "GET", 
                        timeout: float = 15, 
                        **kwargs) -> Union[aiohttp.ClientResponse, None]:
        """`openhivenpy.gateway.HTTP.raw_request()`

        Wrapped HTTP GET request for a specified endpoint. 
        
        Returns the raw ClientResponse object
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..'
                            Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15
        
        method: `str` - HTTP Method that should be used to perform the request
        
        headers: `dict` - Defaults to the normal headers. Note: Changing content type can make the request break.
                            Use with caution!
                
        **kwargs: `any` - Other parameter for requesting.
                        See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        # Timeout Handler that watches if the request takes too long
        async def _time_out_handler(_timeout: float) -> None:
            start_time = time.time()
            timeout_limit = start_time + _timeout
            while True:
                if self._request.done():
                    break
                elif time.time() > timeout_limit:
                    if not self._request.cancelled():
                        self._request.cancel()
                    logger.error(f"[HTTP] >> FAILED HTTP '{method.upper()}' with endpoint: "
                                 f"{endpoint}; Request to Hiven timed out!")
                    break
                await asyncio.sleep(0.25)
            return None

        async def _request(endpoint, method, **kwargs):
            # Deactivated because of errors that occurred using it!
            _timeout = aiohttp.ClientTimeout(total=None)
            if self._ready:
                try:
                    error = False
                    if kwargs.get('headers') is None:
                        headers = self.headers
                    else:
                        headers = kwargs.pop('headers')
                    url = f"{self.api_url}{endpoint}"
                    async with self.session.request(
                                                    method=method,
                                                    url=url,
                                                    headers=headers, 
                                                    timeout=_timeout,
                                                    **kwargs) as resp:
                        http_code = resp.status

                        hiven_error_code = None
                        hiven_error_reason = None

                        # If the response code is lower than 300 the request was somewhat successful
                        if http_code < 300:
                            data = await resp.read()
                            if http_code == 204:
                                if method == "GET":
                                    error = True
                                logger.warning("[HTTP] << Received Empty HTTP Response")
                            else:
                                json = json_decoder.loads(data)
                                
                                error = json.get('error', False)
                                if error:
                                    hiven_error_code = json['error'].get('code')
                                    hiven_error_reason = json['error'].get('message')
                                else:
                                    hiven_error_code = 'Unknown HTTP or Request Error'
                                    hiven_error_reason = 'Possibly faulty request or response!'

                            if error is False:
                                return resp
                                
                        error_code = http_code
                        error_reason = resp.reason

                        logger.warning(f"[HTTP] << FAILED HTTP '{method.upper()}' with endpoint: " 
                                     f"{endpoint}; {error_code}, {error_reason}")
                        if hiven_error_code or hiven_error_reason:
                            logger.warning(f"[HTTP] << Received Hiven Error: {hiven_error_code} - {hiven_error_reason}")

                        return resp

                except Exception as e:
                    logger.error(f"[HTTP] << FAILED HTTP '{method.upper()}' with endpoint: {endpoint}; "
                                 f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")
                        
            else:
                logger.error(f"[HTTP] << The HTTPClient was not ready when trying to HTTP {method}!" 
                             "The connection is either faulty initialized or closed!")
                return None    

        self._request = self.loop.create_task(_request(endpoint, method, **kwargs))
        _task_time_out_handler = self.loop.create_task(_time_out_handler(timeout))

        try:
            resp = await asyncio.gather(self._request, _task_time_out_handler)
        except asyncio.CancelledError:
            logger.warning(f"[HTTP] >> Request was cancelled!")
            return
        except Exception as e:
            logger.error(f"[HTTP] >> FAILED HTTP '{method.upper()}' with endpoint: {self.host}{endpoint};" 
                         f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.HTTPError(f"An error occurred while performing HTTP '{method.upper()}' with endpoint:" 
                                 f"{self.host}{endpoint}; {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        return resp[0]
    
    async def request(self, endpoint: str, *, json: dict = None, timeout: float = 15, **kwargs) -> Union[dict, None]:
        """`openhivenpy.gateway.HTTP.request()`

        Wrapped HTTP request for a specified endpoint. 
        
        Returns a python dictionary containing the response data if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..'
                            Will be appended to the standard link: 'https://api.hiven.io/version'

        json: `str` - JSON format data that will be appended to the request

        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15

        headers: `dict` - Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!

        **kwargs: `any` - Other parameter for requesting.
                        See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        resp = await self.raw_request(endpoint, method="GET", timeout=timeout, **kwargs)
        if resp is not None and resp.status < 300:
            if resp.status < 300 and resp.status != 204:
                return await resp.json()
            else:
                return None
        else:
            return None
    
    async def post(self, endpoint: str, *, json: dict = None, timeout: float = 15, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTP.post()`

        Wrapped HTTP Post for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..'
                            Will be appended to the standard link: 'https://api.hiven.io/version'

        json: `str` - JSON format data that will be appended to the request

        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15

        headers: `dict` - Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!

        **kwargs: `any` - Other parameter for requesting.
                        See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        return await self.raw_request(
                                    endpoint, 
                                    method="POST", 
                                    json=json, 
                                    timeout=timeout,
                                    **kwargs)
            
    async def delete(self, endpoint: str, *, timeout: int = 10, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTP.delete()`

        Wrapped HTTP delete for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..'
                            Will be appended to the standard link: 'https://api.hiven.io/version'

        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15

        headers: `dict` - Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!

        **kwargs: `any` - Other parameter for requesting.
                        See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info

        """
        return await self.raw_request(
                                    endpoint, 
                                    method="DELETE", 
                                    timeout=timeout, 
                                    **kwargs)
        
    async def put(self, endpoint: str, *, json: dict = None, timeout: float = 15, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTP.put()`

        Wrapped HTTP put for a specified endpoint.
        
        Similar to post, but multiple requests do not affect performance
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..'
                            Will be appended to the standard link: 'https://api.hiven.io/version'

        json: `str` - JSON format data that will be appended to the request

        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15

        headers: `dict` - Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!

        **kwargs: `any` - Other parameter for requesting.
                        See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info

        """
        headers = dict(self.headers)
        headers['Content-Type'] = 'application/json'
        return await self.raw_request(
                                    endpoint, 
                                    method="PUT", 
                                    json=json, 
                                    timeout=timeout, 
                                    headers=headers,
                                    **kwargs)
        
    async def patch(self, endpoint: str, *, json: dict = None, timeout: float = 15, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTP.patch()`

        Wrapped HTTP patch for a specified endpoint.
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..'
                            Will be appended to the standard link: 'https://api.hiven.io/version'

        json: `str` - JSON format data that will be appended to the request

        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15

        headers: `dict` - Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!

        **kwargs: `any` - Other parameter for requesting.
                        See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info

        """
        headers = dict(self.headers)
        headers['Content-Type'] = 'application/json'
        return await self.raw_request(
                                    endpoint, 
                                    method="PATCH", 
                                    json=json, 
                                    timeout=timeout, 
                                    headers=headers,
                                    **kwargs)
    
    async def options(self, endpoint: str, *, json: dict = None, timeout: float = 15, **kwargs) -> aiohttp.ClientResponse:
        """`openhivenpy.gateway.HTTP.options()`

        Wrapped HTTP options for a specified endpoint.
        
        Requests permission for performing communication with a URL or server
        
        Returns the ClientResponse object if successful and else returns `None`
        
        Parameter:
        ----------
        
        endpoint: `str` - Url place in url format '/../../..'
                            Will be appended to the standard link: 'https://api.hiven.io/version'
    
        json: `str` - JSON format data that will be appended to the request
        
        timeout: `int` - Time the server has time to respond before the connection timeouts. Defaults to 15
        
        headers: `dict` - Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!
        
        **kwargs: `any` - Other parameter for requesting.
                        See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        
        """
        return await self.raw_request(
                                    endpoint, 
                                    method="OPTIONS", 
                                    json=json, 
                                    timeout=timeout, 
                                    **kwargs)
    