"""Aiohttp client class utility."""
import asyncio
import logging
from socket import AF_INET

import aiohttp
from aiohttp.client import _RequestOptions

SIZE_POOL_AIOHTTP = 100


class AiohttpClient(object):
    """Aiohttp session client utility.

    Utility class for handling HTTP async request for whole FastAPI application
    scope.

    Attributes:
        sem (asyncio.Semaphore, optional): Semaphore value.
        aiohttp_client (aiohttp.ClientSession, optional): Aiohttp client session
            object instance.

    """

    sem: asyncio.Semaphore | None = None
    aiohttp_client: aiohttp.ClientSession | None = None
    log: logging.Logger = logging.getLogger(__name__)

    @classmethod
    def get_aiohttp_client(cls) -> aiohttp.ClientSession:
        """Create aiohttp client session object instance.

        Returns:
            aiohttp.ClientSession: ClientSession object instance.

        """
        if cls.aiohttp_client is None:
            cls.log.debug("Initialize AiohttpClient session.")
            timeout = aiohttp.ClientTimeout(total=2)
            connector = aiohttp.TCPConnector(
                family=AF_INET,
                limit_per_host=SIZE_POOL_AIOHTTP,
            )
            cls.aiohttp_client = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
            )

        return cls.aiohttp_client

    @classmethod
    async def close_aiohttp_client(cls) -> None:
        """Close aiohttp client session."""
        if cls.aiohttp_client:
            cls.log.debug("Close AiohttpClient session.")
            await cls.aiohttp_client.close()
            cls.aiohttp_client = None

    @classmethod
    async def get(cls, url: str, **kwargs: _RequestOptions) -> aiohttp.ClientResponse:
        """Execute HTTP GET request.

        Args:
            url (str): HTTP GET request endpoint.
            **kwargs (_RequestOptions): Defaults kwargs for aiohttp request

        Returns:
            response: HTTP GET request response - aiohttp.ClientResponse
                object instance.

        """
        client = cls.get_aiohttp_client()

        cls.log.debug(f"Started GET {url}")
        response = await client.get(url, **kwargs)
        return response

    @classmethod
    async def post(cls, url: str, **kwargs: _RequestOptions) -> aiohttp.ClientResponse:
        """Execute HTTP POST request.
        Args:
            url (str): HTTP POST request endpoint.
            **kwargs (_RequestOptions): Defaults kwargs for aiohttp request

        Returns:
            response: HTTP POST request response - aiohttp.ClientResponse object instance.
        """
        client = cls.get_aiohttp_client()

        cls.log.debug(f"Started POST: {url}")
        response = await client.post(url, **kwargs)
        return response

    @classmethod
    async def put(cls, url: str, **kwargs: _RequestOptions) -> aiohttp.ClientResponse:
        """Execute HTTP PUT request.
        Args:
            url (str): HTTP PUT request endpoint.
            **kwargs (_RequestOptions): Defaults kwargs for aiohttp request

        Returns:
            response: HTTP PUT request response - aiohttp.ClientResponse object instance.
        """
        client = cls.get_aiohttp_client()

        cls.log.debug(f"Started PUT: {url}")
        response = await client.put(url, **kwargs)
        return response

    @classmethod
    async def delete(cls, url: str, **kwargs: _RequestOptions) -> aiohttp.ClientResponse:
        """Execute HTTP DELETE request.
        Args:
            url (str): HTTP DELETE request endpoint.
            **kwargs (_RequestOptions): Defaults kwargs for aiohttp request
        Returns:
            response: HTTP DELETE request response - aiohttp.ClientResponse object instance.
        """
        client = cls.get_aiohttp_client()

        cls.log.debug(f"Started DELETE: {url}")
        response = await client.delete(url, **kwargs)
        return response

    @classmethod
    async def patch(cls, url: str, **kwargs: _RequestOptions) -> aiohttp.ClientResponse:
        """Execute HTTP PATCH request.
        Args:
            url (str): HTTP PATCH request endpoint.
            **kwargs (_RequestOptions): Defaults kwargs for aiohttp request

        Returns:
            response: HTTP PATCH request response - aiohttp.ClientResponse
                object instance.
        """
        client = cls.get_aiohttp_client()

        cls.log.debug(f"Started PATCH: {url}")
        response = await client.patch(url, **kwargs)
        return response
