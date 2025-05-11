import abc


class IAsyncHttpClient(abc.ABC):
    """
    Interface for an asynchronous HTTP client.

    This interface defines a standard contract for making HTTP requests asynchronously.
    It abstracts over specific libraries (e.g. aiohttp, httpx) to allow interchangeable implementations.

    Methods:
        get(url: str, **kwargs): Perform an HTTP GET request.
        post(url: str, **kwargs): Perform an HTTP POST request.
        put(url: str, **kwargs): Perform an HTTP PUT request.
        delete(url: str, **kwargs): Perform an HTTP DELETE request.
        patch(url: str, **kwargs): Perform an HTTP PATCH request.
    """

    @abc.abstractmethod
    async def get(self, url: str, **kwargs): ...

    @abc.abstractmethod
    async def post(self, url: str, **kwargs): ...

    @abc.abstractmethod
    async def put(self, url: str, **kwargs): ...

    @abc.abstractmethod
    async def delete(self, url: str, **kwargs): ...

    @abc.abstractmethod
    async def patch(self, url: str, **kwargs): ...
