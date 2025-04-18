from asyncio import TimeoutError
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Literal, TypeAlias, TYPE_CHECKING

import requests
from aiohttp import ClientSession
from requests.exceptions import Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt


HttpMethod: TypeAlias = Literal[
    "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"
]


class HttpClient:
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
    def request(self, method: HttpMethod, url: str, **kwargs: Any) -> dict:
        """Synchronous HTTP request with retry support."""
        client = self.session or requests
        response = client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

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
    async def arequest(self, method: HttpMethod, url: str, **kwargs: Any) -> dict:
        """A request wrapper. Mainly for retrying."""
        async with self._with_asession() as session:
            async with await session.request(method, url, **kwargs) as response:
                return await response.json()

    def __getattr__(self, name: str):
        """Dynamically handle HTTP methods like get(), post(), etc."""
        sync_methods = ["get", "post", "put", "patch", "delete", "head", "options"]
        async_methods = [f"a{method}" for method in sync_methods]

        # Handle sync methods (e.g., get(), post(), etc.)
        if name.lower() in sync_methods:

            def method(url: str, **kwargs: Any):
                return self.request(name.upper(), url, **kwargs)

            return method

        # Handle async methods (e.g., aget(), apost(), etc.)
        if name.lower() in async_methods:

            def method(url: str, **kwargs: Any):
                return self.arequest(name[1:].upper(), url, **kwargs)

            return method

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    if TYPE_CHECKING:

        def get(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        def options(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        def head(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        def post(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        def put(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        def patch(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        def delete(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        async def aget(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        async def aoptions(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        async def ahead(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        async def apost(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        async def aput(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        async def apatch(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...

        async def adelete(
            self,
            url: str,
            **kwargs: Any,
        ) -> dict: ...
