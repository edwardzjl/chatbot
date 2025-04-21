from asyncio import TimeoutError
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Literal, TypeAlias, TYPE_CHECKING

import requests
from aiohttp import ClientSession
from aiohttp.client import _RequestContextManager
from requests.exceptions import Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt


HttpMethod: TypeAlias = Literal[
    "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"
]

sync_methods = ["get", "post", "put", "patch", "delete", "head", "options"]
async_methods = [f"a{method}" for method in sync_methods]


class HttpClient:
    """A unified HTTP client wrapper for both synchronous and asynchronous requests.

    This class provides a consistent interface for making HTTP requests, supporting both
    synchronous (using `requests` library) and asynchronous (using `aiohttp` library) operations.
    It is designed to simplify the development process, especially in ecosystems where both sync
    and async functions are required, such as in langchain.

    Features:
    - Supports common HTTP methods (GET, POST, PUT, DELETE, etc.) for both sync and async requests.
    - Automatically retries requests in case of timeouts.
    - Handles session management, making it easier to use `requests.Session` or `aiohttp.ClientSession`.
    - Reduces boilerplate code by dynamically creating method handlers for sync and async operations.

    Usage:
    - For synchronous requests, use the `HttpClient` methods directly (e.g., `client.get()`, `client.post()`).
    - For asynchronous requests, use the corresponding async methods (e.g., `client.aget()`, `client.apost()`).

    Attributes:
        session (requests.Session | None): Optional synchronous requests session.
        asession (aiohttp.ClientSession | None): Optional asynchronous aiohttp session.

    Methods:
        request(method: str, url: str, **kwargs): Performs a synchronous HTTP request with retry support.
        arequest(method: str, url: str, **kwargs): Performs an asynchronous HTTP request with retry support.
    """

    def __init__(
        self,
        session: requests.Session | None = None,
        asession: ClientSession | None = None,
    ):
        """Initialize the HTTP client with optional sessions.

        Args:
            session (requests.Session | None): Optional sync requests session.
            asession (ClientSession | None): Optional async aiohttp session.
        """
        self.session = session
        self.asession = asession

    @retry(
        retry=retry_if_exception_type(Timeout),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def request(self, method: HttpMethod, url: str, **kwargs) -> requests.Response:
        """Synchronous HTTP request with retry support."""
        client = self.session or requests
        response = client.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    @asynccontextmanager
    async def _with_asession(self) -> AsyncGenerator[ClientSession, None]:
        """Yield the injected aiohttp session or create a new one."""
        if self.asession:
            yield self.asession
        else:
            async with ClientSession(raise_for_status=True) as session:
                yield session

    @retry(
        retry=retry_if_exception_type(TimeoutError),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def arequest(
        self, method: HttpMethod, url: str, **kwargs
    ) -> _RequestContextManager:
        """A request wrapper. Mainly for retrying."""
        async with self._with_asession() as session:
            return session.request(method, url, **kwargs)

    def __getattr__(self, name: str):
        """Dynamically handle HTTP methods like get(), post(), etc."""
        # Handle sync methods (e.g., get(), post(), etc.)
        if name.lower() in sync_methods:

            def method(*args, **kwargs):
                return self.request(name.upper(), *args, **kwargs)

            return method

        # Handle async methods (e.g., aget(), apost(), etc.)
        if name.lower() in async_methods:

            def method(*args, **kwargs):
                return self.arequest(name[1:].upper(), *args, **kwargs)

            return method

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    if TYPE_CHECKING:

        def get(
            self,
            url: str,
            **kwargs,
        ) -> requests.Response: ...

        def options(
            self,
            url: str,
            **kwargs,
        ) -> requests.Response: ...

        def head(
            self,
            url: str,
            **kwargs,
        ) -> requests.Response: ...

        def post(
            self,
            url: str,
            **kwargs,
        ) -> requests.Response: ...

        def put(
            self,
            url: str,
            **kwargs,
        ) -> requests.Response: ...

        def patch(
            self,
            url: str,
            **kwargs,
        ) -> requests.Response: ...

        def delete(
            self,
            url: str,
            **kwarg,
        ) -> requests.Response: ...

        async def aget(
            self,
            url: str,
            **kwargs,
        ) -> _RequestContextManager: ...

        async def aoptions(
            self,
            url: str,
            **kwargs,
        ) -> _RequestContextManager: ...

        async def ahead(
            self,
            url: str,
            **kwargs,
        ) -> _RequestContextManager: ...

        async def apost(
            self,
            url: str,
            **kwargs,
        ) -> _RequestContextManager: ...

        async def aput(
            self,
            url: str,
            **kwargs,
        ) -> _RequestContextManager: ...

        async def apatch(
            self,
            url: str,
            **kwargs,
        ) -> _RequestContextManager: ...

        async def adelete(
            self,
            url: str,
            **kwargs,
        ) -> _RequestContextManager: ...
