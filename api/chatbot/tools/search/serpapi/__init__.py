import logging
from typing import Literal

from aiohttp import ClientResponseError
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field
from requests.exceptions import HTTPError

from chatbot.http_client import HttpClient
from chatbot.utils import is_public_ip

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
    name: str = "web_search"
    description: str = "Use this tool to perform general web searches to find information on the internet. Use for facts, definitions, explanations, historical information, specific websites, or any query requiring a broad web search. Use only when more specific tools are not appropriate."
    args_schema: ArgsSchema | None = SearchInput
    response_format: Literal["content", "content_and_artifact"] = "content_and_artifact"

    # not using the official SDK
    base_url: str = "https://serpapi.com/search.json"
    engine: str = "google_light"
    api_key: str

    http_client: HttpClient = HttpClient()

    geo_tool: BaseTool | None = None

    def _run(
        self,
        q: str,
        n_results: int = 5,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> tuple[str, dict]:
        params = {
            "engine": self.engine,
            "q": q,
            "start": "0",
            "num": n_results,
            "api_key": self.api_key,
        } | kwargs

        if (
            self.geo_tool
            and (client_ip := run_manager.metadata.get("client_ip")) is not None
            and is_public_ip(client_ip)
        ):
            try:
                location = self.geo_tool.run(client_ip)
                params["location"] = location
            except Exception:
                logger.exception("Failed to get location from IP")

        try:
            resp = self.http_client.get(self.base_url, params=params)
            data = resp.json()
        except HTTPError as http_err:
            raise ToolException(str(http_err))
        else:
            llm_content = self._format_response(data)
            return llm_content, data

    async def _arun(
        self,
        q: str,
        n_results: int = 5,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> tuple[str, dict]:
        params = {
            "engine": self.engine,
            "q": q,
            "start": "0",
            "num": n_results,
            "api_key": self.api_key,
        } | kwargs

        if (
            self.geo_tool
            and (client_ip := run_manager.metadata.get("client_ip")) is not None
            and is_public_ip(client_ip)
        ):
            try:
                location = await self.geo_tool.arun(client_ip)
                params["location"] = location
            except Exception:
                logger.exception("Failed to get location from IP")

        try:
            async with await self.http_client.aget(
                self.base_url, params=params
            ) as resp:
                data = await resp.json()
        except ClientResponseError as http_err:
            raise ToolException(str(http_err))
        else:
            llm_content = self._format_response(data)
            return llm_content, data

    def _format_response(self, data: dict) -> str:
        try:
            model = SearchResult.model_validate(data)
            return model.dump_minimal()
        except Exception:
            logger.exception("Failed to format response")
            return data
