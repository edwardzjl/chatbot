import functools
import logging
from typing import Literal
from typing_extensions import Self
from urllib.parse import urlencode

from aiohttp import ClientResponseError
from aiohttp_client_cache import CachedSession as AsyncCachedSession, SQLiteBackend
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field, model_validator
from requests.exceptions import HTTPError, Timeout
from requests_cache import CachedSession
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from .schema import SearchResult


logger = logging.getLogger(__name__)


class SearchInput(BaseModel):
    """Input params for Search API."""

    q: str = Field(description="Query to search for.")
    n_results: int = Field(
        default=5,
        description="Number of results to return. Default is 5.",
    )


class SearchTool(BaseTool):
    name: str = "search"
    description: str = "Useful for when you need to search the Internet."
    args_schema: ArgsSchema | None = SearchInput
    response_format: Literal["content", "content_and_artifact"] = "content_and_artifact"

    # not using the official SDK
    base_url: str = "https://serpapi.com/search.json"
    engine: str = "google_light"
    api_key: str
    session: CachedSession = CachedSession(
        "serpapi.cache", expire_after=-1, ignored_parameters=["apikey"]
    )
    """Synchronous requests session with cache support."""

    @model_validator(mode="after")
    def patch_request_timeout(self) -> Self:
        # Monkey patch the session to add a global timeout
        self.session.request = functools.partial(self.session.request, timeout=5)
        return self

    def _run(
        self,
        q: str,
        n_results: int = 5,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> tuple[dict, dict]:
        params = {
            "engine": self.engine,
            "q": q,
            "start": "0",
            "num": n_results,
            "api_key": self.api_key,
        } | kwargs

        try:
            data = self._search(params)
        except HTTPError as http_err:
            raise ToolException(str(http_err))
        else:
            data = self._format_response(data)
            return data, {"url": f"{self.base_url}?{urlencode(params)}"}

    @retry(
        retry=retry_if_exception_type((HTTPError, Timeout)), stop=stop_after_attempt(3)
    )
    def _search(self, params: dict) -> dict:
        """A request wrapper. Mainly for retrying."""
        response = self.session.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()

    async def _arun(
        self,
        q: str,
        n_results: int = 5,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> tuple[dict, dict]:
        params = {
            "engine": self.engine,
            "q": q,
            "start": "0",
            "num": n_results,
            "api_key": self.api_key,
        } | kwargs

        try:
            data = await self._asearch(params)
        except ClientResponseError as http_err:
            raise ToolException(str(http_err))
        else:
            data = self._format_response(data)
            return data, {"url": f"{self.base_url}?{urlencode(params)}"}

    @retry(
        retry=retry_if_exception_type((ClientResponseError, TimeoutError)),
        stop=stop_after_attempt(3),
    )
    async def _asearch(self, params: dict) -> dict:
        """A request wrapper. Mainly for retrying."""
        # TODO: The timeout is a bit complicated for aiohttp, using default for now.
        async with AsyncCachedSession(
            cache=SQLiteBackend("searpapi.async.cache"), raise_for_status=True
        ) as session:
            async with await session.get(self.base_url, params=params) as response:
                return await response.json()

    def _format_response(self, data):
        try:
            model = SearchResult.model_validate(data)
            return model.dump_minimal()
        except Exception:
            logger.exception("Failed to format response")
            return data

    def __del__(self):
        """cleanup"""
        self.session.close()
