from urllib.parse import urljoin

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool

from chatbot.http_client import HttpClient


class GeoLocationTool(BaseTool):
    """Get the geolocation of a given IP address or domain name.

    This tool is not for agent usage. It is used internally for other tools (e.g., SearchTool).
    I made it a tool instead of a function because I need both `run` and `arun`.
    """

    name: str = "geolocation"
    description: str = "Useful for when you need to get geo location for an IP address."

    base_url: str = "https://api.ipgeolocation.io"
    api_key: str

    http_client: HttpClient = HttpClient()

    @property
    def ipgeo_url(self) -> str:
        """Return the URL for the IP geolocation API."""
        return urljoin(self.base_url, "/ipgeo")

    def _run(
        self,
        ip: str,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> tuple[dict, dict]:
        params = {
            "apiKey": self.api_key,
            "ip": ip,
        }
        resp = self.http_client.get(self.ipgeo_url, params=params)
        data = resp.json()
        return ", ".join([data["city"], data["state_prov"], data["country_name"]])

    async def _arun(
        self,
        ip: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> str:
        params = {
            "apiKey": self.api_key,
            "ip": ip,
        }
        async with await self.http_client.aget(self.ipgeo_url, params=params) as resp:
            data = await resp.json()
        return ", ".join([data["city"], data["state_prov"], data["country_name"]])
