import ipaddress
import logging
from urllib.parse import urlparse

from aiohttp import ClientResponseError
from bs4 import BeautifulSoup, Comment
from fake_useragent import UserAgent
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from langchain_core.tools.base import ArgsSchema
from markdownify import markdownify as md
from pydantic import BaseModel, Field, field_validator
from requests.exceptions import HTTPError

from chatbot.http_client import HttpClient


logger = logging.getLogger(__name__)


class BrowserInput(BaseModel):
    """Input params for BrowserTool."""

    url: str = Field(description="The url you want to visit.")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL scheme must be http or https")
        hostname = parsed.hostname or ""
        try:
            addr = ipaddress.ip_address(hostname)
            if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
                raise ValueError("Requests to private/internal addresses are not allowed")
        except ValueError as exc:
            if "not allowed" in str(exc):
                raise
            # hostname is a domain name; block well-known internal names
            if hostname in ("localhost",) or hostname.endswith(".internal") or hostname.endswith(".local"):
                raise ValueError("Requests to internal hostnames are not allowed")
        return v


ua = UserAgent()


class BrowserTool(BaseTool):
    name: str = "web_browser"
    description: str = "You can use this tool to retrieve the full content of a webpage, cleaned and formatted as Markdown."
    args_schema: ArgsSchema | None = BrowserInput

    http_client: HttpClient = HttpClient()

    def _run(
        self,
        url: str,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> str:
        try:
            # Some sites block requests from requests without a user agent header.
            resp = self.http_client.get(url, headers={"User-Agent": ua.random})
        except HTTPError as http_err:
            raise ToolException(str(http_err))
        else:
            content = resp.content
            return self._process(content)

    async def _arun(
        self,
        url: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> str:
        try:
            # Some sites block requests from requests without a user agent header.
            async with await self.http_client.aget(
                url, headers={"User-Agent": ua.random}
            ) as resp:
                content = await resp.read()
                return self._process(content)
        except ClientResponseError as http_err:
            raise ToolException(str(http_err))

    def _process(self, result: str) -> str:
        soup = BeautifulSoup(result, "html.parser")

        for script_or_style in soup(["meta", "script", "style"]):
            script_or_style.decompose()

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        return md(str(soup), heading_style="ATX")
