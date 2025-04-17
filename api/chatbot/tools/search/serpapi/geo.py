import functools
from typing_extensions import Self
from urllib.parse import urljoin

from aiohttp import ClientTimeout, ClientResponseError
from aiohttp_client_cache import CachedSession as AsyncCachedSession, SQLiteBackend
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import model_validator
from requests.exceptions import HTTPError, Timeout
from requests_cache import CachedSession
from tenacity import retry, retry_if_exception_type, stop_after_attempt


class GeoLocationTool(BaseTool):
    """Get the geolocation of a given IP address or domain name.

    This tool is not for agent usage. It is used internally for other tools (e.g., SearchTool).
    I made it a tool instead of a function because I need both `run` and `arun`.
    """

    name: str = "geolocation"
    description: str = "Useful for when you need to get geo location for an IP address."

    base_url: str = "https://api.ipgeolocation.io"
    api_key: str
    timeout: int | None = 5
    """Timeout in seconds for both sync and async requests. Default: 5 seconds."""
    session: CachedSession = CachedSession(
        "ipgeolocation.cache", expire_after=-1, ignored_parameters=["apiKey"]
    )
    """Synchronous requests session with cache support."""

    @model_validator(mode="after")
    def patch_request_timeout(self) -> Self:
        # Monkey patch the session to add a global 5 seconds timeout
        # See <https://requests.readthedocs.io/en/latest/user/advanced/#timeouts>
        if self.timeout:
            self.session.request = functools.partial(
                self.session.request, timeout=self.timeout
            )
        return self

    @retry(
        retry=retry_if_exception_type((HTTPError, Timeout)), stop=stop_after_attempt(3)
    )
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
        url = urljoin(self.base_url, "/ipgeo")
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return ", ".join([data["city"], data["state_prov"], data["country_name"]])

    @retry(
        retry=retry_if_exception_type((ClientResponseError, TimeoutError)),
        stop=stop_after_attempt(3),
    )
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
        timeout = ClientTimeout(total=5)
        async with AsyncCachedSession(
            base_url=self.base_url,
            timeout=timeout,
            raise_for_status=True,
            cache=SQLiteBackend("ipgeolocation.async.cache"),
        ) as session:
            async with await session.get("/ipgeo", params=params) as response:
                data = await response.json()
        return ", ".join([data["city"], data["state_prov"], data["country_name"]])
