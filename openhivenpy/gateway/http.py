import aiohttp
import asyncio
import logging
import sys
import time
import os
import json as json_decoder
from yarl import URL
import typing

__all__ = ['HTTP']

from .. import utils
from ..exception import HTTPError, SessionCreateError

logger = logging.getLogger(__name__)

# Hiven API endpoint formatting
request_url_format = "https://{0}/{1}"


class HTTPTraceback:
    @staticmethod
    async def on_request_start(session, trace_config_ctx, params):
        logger.debug(f"[HTTP] >> Request with HTTP {params.method} started at {time.time()}")
        logger.debug(f"[HTTP] >> URL >> {params.url}")

    @staticmethod
    async def on_request_end(session, trace_config_ctx, params):
        logger.debug(f"[HTTP] << Request with HTTP {params.method} finished!")
        logger.debug(f"[HTTP] << Header << {params.headers}")
        logger.debug(f"[HTTP] << URL << {params.url}")
        logger.debug(f"[HTTP] << Response << {params.response}")

    @staticmethod
    async def on_request_exception(session, trace_config_ctx, params):
        logger.debug(f"[HTTP] << An exception occurred while executing the request")

    @staticmethod
    async def on_request_redirect(session, trace_config_ctx, params):
        logger.debug(f"[HTTP] << REDIRECTING with URL {params.url} and HTTP {params.method}")

    @staticmethod
    async def on_response_chunk_received(session, trace_config_ctx, params):
        logger.debug(f"[HTTP] << Chunk Received << {params.chunk}\n")

    @staticmethod
    async def on_connection_queued_start(session, trace_config_ctx, params):
        logger.debug(f"[HTTP] >> HTTP {params.method} with {params.url} queued!")


class HTTP:
    """
    HTTP-Client for requests and interaction with the Hiven API
    """
    def __init__(self, client, *, host, api_version, loop):
        """
        :param client: The used HivenClient
        :param loop: Event loop that will be used to execute all async functions. Will use
                           'asyncio.get_event_loop()' to fetch the EventLoop. Will create a new one if no
                           one was created yet
        :param host: Url for the API which will be used to interact with Hiven.
                     Defaults to the pre-set environment host (api.hiven.io)
        :param api_version: Version string for the API Version. Defaults to the pre-set environment version (v1)
        """
        self.client = client
        self.host = host
        self.api_version = api_version
        self.api_url = URL(request_url_format.format(self.host, self.api_version))
        self.headers = {
            "Authorization": client.token,
            "Host": self.host
        }
        self._token = client.token
        self._ready = False
        self._session = None  # Will be created during start of connection
        self._loop = loop

        # Last/Currently executed/ing request
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
    def token(self) -> str:
        return getattr(self, '_token', None)

    @property
    def ready(self) -> bool:
        return getattr(self, '_ready', False)

    @property
    def session(self):
        return getattr(self, '_session', None)

    @property
    def loop(self):
        return getattr(self, '_loop', None)

    async def connect(self) -> typing.Union[aiohttp.ClientSession, None]:
        """
        Establishes for the HTTP a connection to Hiven

        :return: The created aiohttp.ClientSession
        """
        try:
            trace_config = aiohttp.TraceConfig()
            trace_config.on_request_start.append(HTTPTraceback.on_request_start)
            trace_config.on_request_end.append(HTTPTraceback.on_request_end)
            trace_config.on_request_exception.append(HTTPTraceback.on_request_exception)
            trace_config.on_request_redirect.append(HTTPTraceback.on_request_redirect)
            trace_config.on_connection_queued_start.append(HTTPTraceback.on_connection_queued_start)
            trace_config.on_response_chunk_received.append(HTTPTraceback.on_response_chunk_received)

            self._session = aiohttp.ClientSession(trace_configs=[trace_config])
            self._ready = True

            resp = await self.request("/users/@me", timeout=30)
            if resp:
                logger.info("[HTTP] Session was successfully created!")
                self.client.storage.update_client_user(resp['data'])
                return self.session
            else:
                # If the request failed it will return None and log a warning
                logger.warning("[HTTP] Test Request for HTTP Initialisation failed! ")
                return None

        except Exception as e:
            utils.log_traceback(
                msg="[HTTP] Traceback:",
                suffix=f"Failed to create HTTP-Session: \n> {sys.exc_info()[0].__name__}: {e}")
            self._ready = False
            await self.session.close()
            raise SessionCreateError(f"Failed to create HTTP-Session! > {sys.exc_info()[0].__name__}: {e}")

    async def close(self) -> bool:
        """
        Closes the HTTP session that is currently connected to Hiven!

        :return: True if it was successful else False
        """
        try:
            await self.session.close()
            self._ready = False
            return True

        except Exception as e:
            utils.log_traceback(
                msg="[CONNECTION] Traceback:",
                suffix=f"[HTTP] Failed to close HTTP Session: {sys.exc_info()[0].__name__}: {e}"
            )
            return False

    async def raw_request(
            self,
            endpoint: str,
            *,
            method: typing.Optional[str] = "GET",
            json: typing.Optional[dict] = None,
            timeout: typing.Optional[int] = 15,
            headers: typing.Optional[dict] = None,  # Defaults to an empty header
            **kwargs) -> typing.Union[aiohttp.ClientResponse, None]:
        """
        Wrapped HTTP request for a specified endpoint.
        
        :param endpoint: Url place in url format '/../../..' Will be appended to the standard link:
                        'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the connection timeouts. Defaults to 15
        :param method: HTTP Method that should be used to perform the request
        :param headers: Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!
        :param kwargs: Other parameter for requesting.
                       See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        :return: Returns the aiohttp.ClientResponse object
        """
        async def http_request(_endpoint: str,
                               _method: str,
                               _json: dict,
                               _headers: dict,
                               **_kwargs) -> typing.Union[aiohttp.ClientResponse, None]:
            """
            The Function that stores the request and the handling of exceptions! Will be used as
            a variable so the status of the request can be seen by the asyncio.Task status!

            :param _endpoint: Endpoint of the request
            :param _method: HTTP method of the request
            :param _json: Additional JSON Data if it exists
            :param _headers: Headers that will be sent! Defaults to the ones that were created during initialisation
            :param _kwargs: Additional Parameter for the aiohttp HTTP Request
            :return: Returns the aiohttp.ClientResponse object
            """
            if self._ready:
                try:
                    # Creating a new ClientTimeout Instance which will default to None since the Timeout was reported
                    # to cause errors! Timeouts are therefore handled in a regular `asyncio.wait_for`
                    _timeout = aiohttp.ClientTimeout(total=None)

                    _headers = self.headers if _headers is None else _headers
                    url = f"{self.api_url.human_repr()}{_endpoint}"
                    async with self.session.request(
                        method=_method, url=url, headers=_headers, timeout=_timeout, json=_json, **_kwargs
                    ) as _resp:
                        http_resp_code = _resp.status
                        data = await _resp.read()  # Raw response data

                        if data:
                            _json_data = json_decoder.loads(data)  # Loading the data in json => will fail if not json
                            _success = _json_data.get('success')  # Fetching the success item <== bool

                            if _success:
                                logger.debug(
                                    f"[HTTP] {http_resp_code} - Request was successful and received expected data!")
                            else:
                                # If an error occurred the response body will contain an error field
                                _error = _json_data.get('error')
                                if _error:
                                    err_code = _error.get('code')
                                    err_msg = _error.get('message')
                                    logger.error(f"[HTTP] Failed HTTP request '{_method.upper()}'! {http_resp_code} -> "
                                                 f"'{err_code}': '{err_msg}'")
                                else:
                                    logger.error(f"[HTTP] Failed HTTP request '{_method.upper()}'! {http_resp_code} -> "
                                                 f"Response: None")
                        else:
                            if http_resp_code != 204:
                                logger.error("[HTTP] Received empty response!")

                        return _resp

                except Exception as _e:
                    utils.log_traceback(
                        msg="[HTTP] Traceback:",
                        suffix=f"HTTP '{_method.upper()}' failed with endpoint: {_endpoint}: \n"
                               f"{sys.exc_info()[0].__name__}, {_e}"
                    )

            else:
                logger.error(f"[HTTP] << The HTTPClient was not ready when trying to perform request with "
                             f"HTTP {_method}! The session is either not initialised or closed!")
                return None

        self._request = asyncio.create_task(http_request(endpoint, method, json, headers, **kwargs))
        try:
            http_client_response = await asyncio.wait_for(self._request, timeout=timeout)

        except asyncio.CancelledError:
            logger.warning(f"[HTTP] >> Request '{method.upper()}' for endpoint '{endpoint}' was cancelled!")
            return

        except asyncio.TimeoutError:
            logger.warning(f"[HTTP] >> Request '{method.upper()}' for endpoint '{endpoint} timeout after {timeout}s!")
            http_client_response = None

        except Exception as e:
            utils.log_traceback(
                msg="[HTTP] Suffix",
                suffix=f"HTTP '{method.upper()}' failed with endpoint: {self.host}{endpoint}: \n"
                       f"{sys.exc_info()[0].__name__}: {e}"
            )
            raise HTTPError(f"HTTP '{method.upper()}' failed with endpoint: "
                            f"{self.host}{endpoint}: {sys.exc_info()[0].__name__}: {e}")

        # Returning the response instance
        return http_client_response

    async def request(self,
                      endpoint: str,
                      *,
                      json: typing.Optional[dict] = None,
                      timeout: typing.Optional[int] = 15,
                      headers: typing.Optional[dict] = None,
                      **kwargs) -> typing.Union[dict, None]:
        """
        Wrapped HTTP 'GET' request for a specified endpoint, which returns only the response data!
        
        :param endpoint: Url place in url format '/../../..' Will be appended to the standard link:
                        'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!
        :param kwargs: Other parameter for requesting.
                       See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        :return: A python dictionary containing the response data if successful and else returns `None`
        """
        resp = await self.raw_request(endpoint, method="GET", timeout=timeout, json=json, headers=headers, **kwargs)
        if resp is not None and resp.status < 300:
            if resp.status < 300 and resp.status != 204:
                # Returning the data in json format (dict)
                return await resp.json()
            else:
                return None
        else:
            return None

    async def get(self,
                  endpoint: str,
                  *,
                  json: typing.Optional[dict] = None,
                  timeout: typing.Optional[int] = 15,
                  headers: typing.Optional[dict] = None,
                  **kwargs) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'GET' request for a specified endpoint

        :param endpoint: Url place in url format '/../../..' Will be appended to the standard link:
                        'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!
        :param kwargs: Other parameter for requesting.
                       See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        :return: Returns the ClientResponse object if successful and else returns `None`
        """
        return await self.raw_request(
            endpoint,
            method="POST",
            json=json,
            headers=headers,
            timeout=timeout,
            **kwargs)

    async def post(self,
                   endpoint: str,
                   *,
                   json: typing.Optional[dict] = None,
                   timeout: typing.Optional[int] = 15,
                   headers: typing.Optional[dict] = None,
                   **kwargs) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'POST' for a specified endpoint.
        
        :param endpoint: Url place in url format '/../../..' Will be appended to the standard link:
                        'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!
        :param kwargs: Other parameter for requesting.
                       See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        :return: Returns the ClientResponse object if successful and else returns `None`
        """
        # If no custom headers were passed a new one will be created and used
        if headers is None:
            # Creating a duplicate header of the default one
            headers = dict(self.headers)

            # Requires the Content-Type to be specified since else it cannot
            # recognise the json-data in the body!
            headers['Content-Type'] = 'application/json'

        return await self.raw_request(
            endpoint,
            method="POST",
            json=json,
            headers=headers,
            timeout=timeout,
            **kwargs)

    async def delete(self,
                     endpoint: str,
                     *,
                     json: typing.Optional[dict] = None,
                     timeout: typing.Optional[int] = 15,
                     headers: typing.Optional[dict] = None,
                     **kwargs) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'DELETE' for a specified endpoint.
        
        :param endpoint: Url place in url format '/../../..' Will be appended to the standard link:
                        'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!
        :param kwargs: Other parameter for requesting.
                       See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        :return: Returns the ClientResponse object if successful and else returns `None`
        """
        return await self.raw_request(
            endpoint,
            method="DELETE",
            json=json,
            timeout=timeout,
            headers=headers,
            **kwargs)

    async def put(self,
                  endpoint: str,
                  *,
                  json: typing.Optional[dict] = None,
                  timeout: typing.Optional[int] = 15,
                  headers: typing.Optional[dict] = None,
                  **kwargs) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'PUT' for a specified endpoint.
        
        Similar to post, but multiple requests do not affect performance

        :param endpoint: Url place in url format '/../../..' Will be appended to the standard link:
                        'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!
        :param kwargs: Other parameter for requesting.
                       See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        :return: Returns the ClientResponse object if successful and else returns `None`
        """
        # If no custom headers were passed a new one will be created and used
        if headers is None:
            # Creating a duplicate header of the default one
            headers = dict(self.headers)

            # Requires the Content-Type to be specified since else it cannot
            # recognise the json-data in the body!
            headers['Content-Type'] = 'application/json'

        return await self.raw_request(
            endpoint,
            method="PUT",
            json=json,
            timeout=timeout,
            headers=headers,  # Passing the new header for the request
            **kwargs)

    async def patch(self,
                    endpoint: str,
                    *,
                    json: typing.Optional[dict] = None,
                    timeout: typing.Optional[int] = 15,
                    headers: typing.Optional[dict] = None,
                    **kwargs) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'PATCH' for a specified endpoint.
        
        :param endpoint: Url place in url format '/../../..' Will be appended to the standard link:
                        'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!
        :param kwargs: Other parameter for requesting.
                       See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        :return: Returns the ClientResponse object if successful and else returns `None`
        """
        # If no custom headers were passed a new one will be created and used
        if headers is None:
            # Creating a duplicate header of the default one
            headers = dict(self.headers)

            # Requires the Content-Type to be specified since else it cannot
            # recognise the json-data in the body!
            headers['Content-Type'] = 'application/json'

        return await self.raw_request(
            endpoint,
            method="PATCH",
            json=json,
            headers=headers,
            timeout=timeout,
            **kwargs)

    async def options(self,
                      endpoint: str,
                      *,
                      json: typing.Optional[dict] = None,
                      timeout: typing.Optional[int] = 15,
                      headers: typing.Optional[dict] = None,
                      **kwargs) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'OPTIONS' for a specified endpoint.
        
        Requests permission for performing communication with a URL or server
        
        :param endpoint: Url place in url format '/../../..' Will be appended to the standard link:
                        'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content type can make the request break.
                        Use with caution!
        :param kwargs: Other parameter for requesting.
                       See https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession for more info
        :return: Returns the ClientResponse object if successful and else returns `None`
        """
        return await self.raw_request(
            endpoint,
            method="OPTIONS",
            json=json,
            headers=headers,
            timeout=timeout,
            **kwargs)
