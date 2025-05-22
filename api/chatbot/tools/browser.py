import logging

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
from pydantic import BaseModel, Field
from requests.exceptions import HTTPError

from chatbot.http_client import HttpClient


logger = logging.getLogger(__name__)


class BrowserInput(BaseModel):
    """Input params for BrowserTool."""

    url: str = Field(description="The url you want to visit.")


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
