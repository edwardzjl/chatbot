from abc import ABC
from asyncio import TimeoutError
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import requests
from aiohttp import ClientSession, ClientResponseError
from langchain_core.tools import BaseTool
from requests.exceptions import HTTPError, Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt


class HttpTool(BaseTool, ABC):
    session: requests.Session | None = None
    """Synchronous requests session. Optional.
    If not provided, the synchronous `run` will send one-shot requests instead.
    """
    asession: ClientSession | None = None
    """Asynchronous requests session. Optional.
    If not provided, the asynchronous `arun` will create a new session for each request.
    """

    @retry(
        retry=retry_if_exception_type((HTTPError, Timeout)),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _req(self, url: str, params: dict) -> dict:
        """A request wrapper. Mainly for retrying."""
        client = self.session or requests.get
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @asynccontextmanager
    async def _with_asession(self) -> AsyncGenerator[ClientSession, None]:
        """Yield either the injected session or a new temporary session."""
        if self.asession:
            yield self.asession
        else:
            async with ClientSession(raise_for_status=True) as session:
                yield session

    @retry(
        retry=retry_if_exception_type((ClientResponseError, TimeoutError)),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _areq(self, url: str, params: dict) -> dict:
        """A request wrapper. Mainly for retrying."""
        async with self._with_asession() as session:
            async with await session.get(url, params=params) as response:
                return await response.json()
