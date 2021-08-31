"""
HTTP Module managing request and the connection to Hiven

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
# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import asyncio
import json as json_decoder
import logging
import sys
import time
from typing import Optional, Union

import aiohttp
from yarl import URL

__all__ = ['HTTP']

from ..base_types import HivenObject
from .. import utils
from ..exceptions import (HTTPError, SessionCreateError,
                          HTTPFailedRequestError, HTTPRequestTimeoutError,
                          HTTPReceivedNoDataError, HTTPSessionNotReadyError,
                          HTTPNotFoundError, HTTPInternalServerError,
                          HTTPRateLimitError)

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

# Hiven API endpoint formatting
request_url_format = "https://{0}/{1}"


class HTTPTraceback(HivenObject):
    @staticmethod
    async def on_request_start(session, trace_config_ctx, params):
        logger.debug(
            f"[HTTP] >> Request with HTTP {params.method} started at {time.time()}")
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
    """ HTTP-Client for requests and interaction with the Hiven API """

    def __init__(self, client: HivenClient, *, host: str, api_version: str):
        """
        :param client: The used HivenClient
        :param host: Url for the API which will be used to interact with Hiven.
         Defaults to the pre-set environment host (api.hiven.io)
        :param api_version: Version string for the API Version. Defaults to the
         pre-set environment version (defaults to v1)
        """
        self.client = client
        self.host = host
        self.api_version = api_version
        self.api_url = URL(
            request_url_format.format(self.host, self.api_version)
        )
        self.headers = {
            "Authorization": client.token,
            "Host": self.host
        }
        self._ready = False
        self._session = None  # Will be created during start of connection

        # Current request/Latest request
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
    def token(self) -> Optional[str]:
        return getattr(self.client, 'token', None)

    @property
    def ready(self) -> Optional[bool]:
        return getattr(self, '_ready', False)

    @property
    def session(self) -> Optional[aiohttp.ClientSession]:
        """ Returns the aiohttp ClientSession instance """
        return getattr(self, '_session', None)

    @property
    def loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """ Returns the Asyncio Event-loop """
        return getattr(self.client, '_loop', None)

    async def connect(self) -> Optional[aiohttp.ClientSession]:
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

            resp = await self.get("/users/@me", timeout=30)
            resp_json: dict = await resp.json()

            logger.info("[HTTP] Session was successfully created!")
            self.client.storage.update_client_user(resp_json['data'])
            return self.session

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to create HTTP-Session:",
                exc_info=sys.exc_info()
            )
            self._ready = False
            await self.session.close()

            raise SessionCreateError(f"Failed to create HTTP-Session") from e

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
                brief=f"[HTTP] Failed to close HTTP Session:",
                exc_info=sys.exc_info()
            )
            raise RuntimeError("Failed to stop the HTTP client") from e

    async def http_request(
            self,
            endpoint: str,
            method: str,
            json: dict,
            headers: dict,
            retry_on_rate_limit: bool,
            **kwargs
    ) -> Union[aiohttp.ClientResponse, None]:
        """
        The Function that stores the request and the handling of
        exceptions! Will be used as a variable so the status of the request
        can be seen by the asyncio.Task status!

        :param endpoint: Endpoint of the request
        :param method: HTTP method of the request
        :param json: Additional JSON Data if it exists
        :param headers: Headers that will be sent! Defaults to the ones
         that were created during initialisation
        :param kwargs: Additional Parameter for the aiohttp HTTP Request
        :param retry_on_rate_limit: Should the request retry after a
         rate_limit was received.
        :return: Returns the aiohttp.ClientResponse object
        :raises HTTPNotFoundError: If 404 is returned
        :raises HTTPRateLimitError: If a rate-limit is received (429) and
         retry_on_rate_limit is False
        :raises HTTPInternalServerError: If 5** is returned
        :raises HTTPReceivedNoDataError: If no data is returned and the code is
         not 204 (no data)
        :raises HTTPFailedRequestError: If no success object is returned
        """

        if not self._ready:
            raise HTTPSessionNotReadyError()

        # Creating a new ClientTimeout Instance which will default to None
        # since the Timeout was reported to cause errors! Timeouts are
        # therefore handled in a regular `asyncio.wait_for`
        _timeout = aiohttp.ClientTimeout(total=None)

        headers = self.headers if headers is None else headers
        url: False = f"{self.api_url.human_repr()}{endpoint}"

        while True:
            async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=_timeout,
                    json=json,
                    **kwargs
            ) as _resp:
                http_resp_code = _resp.status
                data = await _resp.read()  # Raw response data

                if http_resp_code == 404:
                    raise HTTPNotFoundError()
                elif http_resp_code == 429:
                    logger.debug(
                        f"[HTTP] {http_resp_code} - "
                        f"Received rate-limit! Param 'retry_on_rate_limit' is "
                        f"{retry_on_rate_limit}"
                    )

                    if retry_on_rate_limit is False:
                        raise HTTPRateLimitError()

                    if data:
                        # "rate_limit", { "expires_at": "<unix-timestamp>"}
                        _json_data = json_decoder.loads(data)

                        unix_ts = time.time()
                        retry_after: int = utils.safe_convert(
                            dtype=int,
                            value=_json_data.get("expires_at"),
                            default=5
                        ) - unix_ts
                    else:
                        retry_after: int = 5

                    # min additional 0.1s
                    await asyncio.sleep(retry_after + 0.1)
                    continue
                elif http_resp_code >= 500:
                    raise HTTPInternalServerError(
                        f"Failed to perform request due to Hiven internal "
                        f"server error [Code: {http_resp_code}]"
                    )

                if not data:
                    if http_resp_code != 204:
                        raise HTTPReceivedNoDataError(
                            "Received empty response from the Hiven "
                            "Servers"
                        )

                # Loading the data in json => will fail if not json
                _json_data = json_decoder.loads(data)
                # Fetching the success item <== bool
                _success = _json_data.get('success')

                if _success:
                    logger.debug(
                        f"[HTTP] {http_resp_code} - "
                        f"Request was successful and received expected "
                        f"data"
                    )
                    return _resp
                else:
                    # If an error occurred the response body will contain
                    # an error field
                    _error = _json_data.get('error')
                    if _error:
                        err_code = _error.get('code')
                        err_msg = _error.get('message')

                        raise HTTPFailedRequestError(
                            f"Failed HTTP request with {http_resp_code} -> "
                            f"'{err_code}': '{err_msg}'"
                        )
                    else:
                        raise HTTPFailedRequestError(
                            f"Failed HTTP request with {http_resp_code} -> "
                            f"Response: None "
                        )

    async def raw_request(
            self,
            endpoint: str,
            *,
            method: Optional[str] = "GET",
            json: Optional[dict] = None,
            timeout: Optional[int] = 15,
            headers: Optional[dict] = None,  # Defaults to an empty header,
            retry_on_rate_limit: bool = True,
            **kwargs
    ) -> Union[aiohttp.ClientResponse, None]:
        """
        Wrapped HTTP request for a specified endpoint.
        
        :param endpoint: Url place in url format '/../../..' Will be appended
         to the standard url: 'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the
         connection timeouts. Defaults to 15
        :param method: HTTP Method that should be used to perform the request
        :param headers: Defaults to the normal headers. Note: Changing content
         type can make the request break. Use with caution!
        :param kwargs: Other parameter for requesting. See
         https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession
         for more info
        :param retry_on_rate_limit: Should the request retry after a rate_limit
         was received. Defaults to True
        :return: Returns the aiohttp.ClientResponse object
        :raises HTTPRequestTimeoutError: If the set timeout is hit
        :raises HTTPError: If any HTTP Error is hit during processing
        """
        try:
            http_client_response = await asyncio.wait_for(
                self.http_request(
                    endpoint, method, json, headers, retry_on_rate_limit,
                    **kwargs
                ),
                timeout=timeout
            )
        except asyncio.CancelledError:
            logger.warning(
                f"[HTTP] >> Request '{method.upper()}' for endpoint "
                f"'{endpoint}' was cancelled!"
            )
            return

        except asyncio.TimeoutError:
            raise HTTPRequestTimeoutError()

        except Exception as e:
            utils.log_traceback(
                brief=f"HTTP '{method.upper()}' failed with endpoint: "
                      f"{self.host}{endpoint}:",
                exc_info=sys.exc_info()
            )
            raise HTTPError(
                f"HTTP '{method.upper()}' failed with endpoint: "
                f"{self.host}{endpoint}: "
            ) from e

        # Returning the response instance
        return http_client_response

    async def get(
            self,
            endpoint: str,
            *,
            json: Optional[dict] = None,
            timeout: Optional[int] = 15,
            headers: Optional[dict] = None,
            retry_on_rate_limit: bool = True,
            **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'GET' request for a specified endpoint

        :param endpoint: Url place in url format '/../../..' Will be appended
         to the standard url: 'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the
         connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content
         type can make the request break. Use with caution!
        :param kwargs: Other parameter for requesting. See
        https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession
         for more info
        :param retry_on_rate_limit: Should the request retry after a rate_limit
         was received. Defaults to True
        :return: Returns the ClientResponse object if successful and else
         returns `None`
        :raises HTTPRequestTimeoutError: If the set timeout is hit
        :raises HTTPError: If any HTTP Error is hit during processing
        """
        return await self.raw_request(
            endpoint,
            method="GET",
            json=json,
            headers=headers,
            timeout=timeout,
            retry_on_rate_limit=retry_on_rate_limit,
            **kwargs
        )

    async def post(
            self,
            endpoint: str,
            *,
            json: Optional[dict] = None,
            timeout: Optional[int] = 15,
            headers: Optional[dict] = None,
            retry_on_rate_limit: bool = True,
            **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'POST' for a specified endpoint.
        
        :param endpoint: Url place in url format '/../../..' Will be appended
         to the standard url: 'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the
         connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content
         type can make the request break. Use with caution!
        :param kwargs: Other parameter for requesting. See
         https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession
         for more info
        :param retry_on_rate_limit: Should the request retry after a rate_limit
         was received. Defaults to True
        :return: Returns the ClientResponse object if successful and else
         returns `None`
        :raises HTTPRequestTimeoutError: If the set timeout is hit
        :raises HTTPError: If any HTTP Error is hit during processing
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
            retry_on_rate_limit=retry_on_rate_limit,
            **kwargs
        )

    async def delete(
            self,
            endpoint: str,
            *,
            json: Optional[dict] = None,
            timeout: Optional[int] = 15,
            headers: Optional[dict] = None,
            retry_on_rate_limit: bool = True,
            **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'DELETE' for a specified endpoint.
        
        :param endpoint: Url place in url format '/../../..' Will be appended
         to the standard url: 'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the
         connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content
         type can make the request break. Use with caution!
        :param kwargs: Other parameter for requesting. See
         https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession
         for more info
        :param retry_on_rate_limit: Should the request retry after a rate_limit
         was received. Defaults to True
        :return: Returns the ClientResponse object if successful and else
         returns `None`
        :raises HTTPRequestTimeoutError: If the set timeout is hit
        :raises HTTPError: If any HTTP Error is hit during processing
        """
        return await self.raw_request(
            endpoint,
            method="DELETE",
            json=json,
            timeout=timeout,
            headers=headers,
            retry_on_rate_limit=retry_on_rate_limit,
            **kwargs
        )

    async def put(
            self,
            endpoint: str,
            *,
            json: Optional[dict] = None,
            timeout: Optional[int] = 15,
            headers: Optional[dict] = None,
            retry_on_rate_limit: bool = True,
            **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'PUT' for a specified endpoint.
        
        Similar to post, but multiple requests do not affect performance

        :param endpoint: Url place in url format '/../../..' Will be appended
         to the standard url: 'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the
         connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content
         type can make the request break. Use with caution!
        :param kwargs: Other parameter for requesting. See
        https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession
         for more info
        :param retry_on_rate_limit: Should the request retry after a rate_limit
         was received. Defaults to True
        :return: Returns the ClientResponse object if successful and else
         returns `None`
        :raises HTTPRequestTimeoutError: If the set timeout is hit
        :raises HTTPError: If any HTTP Error is hit during processing
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
            retry_on_rate_limit=retry_on_rate_limit,
            **kwargs
        )

    async def patch(
            self,
            endpoint: str,
            *,
            json: Optional[dict] = None,
            timeout: Optional[int] = 15,
            headers: Optional[dict] = None,
            retry_on_rate_limit: bool = True,
            **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'PATCH' for a specified endpoint.
        
        :param endpoint: Url place in url format '/../../..' Will be appended
         to the standard url: 'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the
         connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content
         type can make the request break. Use with caution!
        :param kwargs: Other parameter for requesting. See
        https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession
         for more info
        :param retry_on_rate_limit: Should the request retry after a rate_limit
         was received. Defaults to True
        :return: Returns the ClientResponse object if successful and else
         returns `None`
        :raises HTTPRequestTimeoutError: If the set timeout is hit
        :raises HTTPError: If any HTTP Error is hit during processing
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
            retry_on_rate_limit=retry_on_rate_limit,
            **kwargs
        )

    async def options(
            self,
            endpoint: str,
            *,
            json: Optional[dict] = None,
            timeout: Optional[int] = 15,
            headers: Optional[dict] = None,
            retry_on_rate_limit: bool = True,
            **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Wrapped HTTP 'OPTIONS' for a specified endpoint.
        
        Requests permission for performing communication with a URL or server
        
        :param endpoint: Url place in url format '/../../..' Will be appended
         to the standard url: 'https://api.hiven.io/{version}'
        :param json: JSON format data that will be appended to the request
        :param timeout: Time the server has time to respond before the
         connection timeouts. Defaults to 15
        :param headers: Defaults to the normal headers. Note: Changing content
         type can make the request break. Use with caution!
        :param kwargs: Other parameter for requesting. See
         https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession
         for more info
        :param retry_on_rate_limit: Should the request retry after a rate_limit
         was received. Defaults to True
        :return: Returns the ClientResponse object if successful and else
         returns `None`
        :raises HTTPRequestTimeoutError: If the set timeout is hit
        :raises HTTPError: If any HTTP Error is hit during processing
        """
        return await self.raw_request(
            endpoint,
            method="OPTIONS",
            json=json,
            headers=headers,
            timeout=timeout,
            retry_on_rate_limit=retry_on_rate_limit,
            **kwargs
        )
