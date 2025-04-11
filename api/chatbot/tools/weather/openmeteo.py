import functools
import logging
from asyncio import TimeoutError
from collections import namedtuple
from typing import Annotated, Literal
from typing_extensions import Self
from urllib.parse import urlencode, urljoin

from aiohttp import ClientResponseError
from aiohttp_client_cache import CachedSession as AsyncCachedSession, SQLiteBackend
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field, model_validator
from requests_cache import CachedSession
from requests.exceptions import HTTPError, Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt


logger = logging.getLogger(__name__)

# I have opted out a lot of way-too-professional params, and modified some descriptions to reduce noise for LLMs.
# See <https://open-meteo.com/en/docs>
# Note that there's a the small line:
# > Every weather variable available in hourly data, is available as current condition as well.
HourlyParamsType = (
    list[
        Literal[
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "precipitation_probability",
            "weather_code",
            "visibility",
        ]
    ]
    | None
)
hourly_params = """- `temperature_2m`: Air temperature at 2 meters above ground
- `relative_humidity_2m`: Relative humidity at 2 meters above ground
- `apparent_temperature`: Apparent temperature is the perceived feels-like temperature combining wind chill factor, relative humidity and solar radiation
- `precipitation`: Total precipitation (rain, showers, snow)
- `precipitation_probability`: Probability of precipitation with more than 0.1 mm
- `weather_code`: Weather condition
- `visibility`: Viewing distance in meters"""


DailyParamsType = (
    list[
        Literal[
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "precipitation_hours",
            "weather_code",
            "sunrise",
            "sunset",
            "wind_speed_10m_max",
        ]
    ]
    | None
)
# modified
daily_params = """- `temperature_2m_max`: Maximum daily air temperature at 2 meters above ground
- `temperature_2m_min`: Minimum daily air temperature at 2 meters above ground
- `apparent_temperature_max`: Maximum daily apparent temperature
- `apparent_temperature_min`: Minimum daily apparent temperature
- `precipitation_sum`: Sum of daily precipitation (including rain, showers and snowfall)
- `precipitation_hours`: The number of hours with rain
- `weather_code`: Weather condition
- `sunrise`: Sunrise time
- `sunset`: Sunset time
- `wind_speed_10m_max`: Maximum wind speed on a day"""


# Currently referencing <https://open-meteo.com/en/docs>.
# However, depends on the output, might need to reference <https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM> instead.
wmo_description = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: light",
    53: "Drizzle: moderate",
    55: "Drizzle: dense intensity",
    56: "Freezing Drizzle: light",
    57: "Freezing Drizzle: dense intensity",
    61: "Rain: slight",
    63: "Rain: moderate",
    65: "Rain: heavy intensity",
    66: "Freezing Rain: light",
    67: "Freezing Rain: heavy intensity",
    71: "Snow fall: slight",
    73: "Snow fall: moderate",
    75: "Snow fall: heavy intensity",
    77: "Snow grains",
    80: "Rain showers: slight",
    81: "Rain showers: moderate",
    82: "Rain showers: violent",
    85: "Snow showers: slight",
    86: "Snow showers: heavy",
    95: "Thunderstorm: slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

GeoCoding = namedtuple("GeoCoding", ["latitude", "longitude"])


# If I use annotated literals for `current`, `daily` or `hourly`, I still need to describe each value in the description, which increase the length of the system prompt.
# See <https://open-meteo.com/en/docs>
# The docstring will be constructed as openapi description, and will be passed to LLMs, so keep it clean and concise.
class WeatherInput(BaseModel):
    """Input params for Weather Forecast API."""

    location: str = Field(
        description="Location for forecast. Accepts **English** location names or postal codes."
    )
    current: Annotated[
        HourlyParamsType,
        Field(
            description=f"""Specifies which current weather data fields to return:
{hourly_params}
""",
            default=None,
        ),
    ]
    daily: Annotated[
        DailyParamsType,
        Field(
            description=f"""Specifies which daily weather data fields to return.
{daily_params}
""",
            default=None,
        ),
    ]
    hourly: Annotated[
        HourlyParamsType,
        Field(
            description=f"""Specifies which hourly weather data fields to return.
{hourly_params}
""",
            default=None,
        ),
    ]
    past_days: int | None = Field(
        description="Returns data from the past N days. Mutually exclusive with `start_date` and `end_date`",
        strict=True,
        ge=0,
        le=92,
        default=None,
    )
    forecast_days: int | None = Field(
        description="Forecasts data for the next N days. Mutually exclusive with `start_date` and `end_date`",
        strict=True,
        ge=0,
        le=16,
        default=7,
    )
    start_date: str | None = Field(
        description="Forecast start date. Format: YYYY-MM-DD. Defaults to the current date. Mutually exclusive with `past_days` and `forecast_days`",
        pattern=r"\d{4}-\d{2}-\d{2}",
        default=None,
    )
    end_date: str | None = Field(
        description="Forecast end date. Format: YYYY-MM-DD. Must be used with `start_date`. Mutually exclusive with `past_days` and `forecast_days`",
        pattern=r"\d{4}-\d{2}-\d{2}",
        default=None,
    )
    temperature_unit: Literal["celsius", "fahrenheit"] | None = Field(
        description="Temperature unit.", default="celsius"
    )


class WeatherTool(BaseTool):
    name: str = "weather_forcast"
    description: str = "Useful for when you need to access weather data."
    args_schema: ArgsSchema | None = WeatherInput
    response_format: Literal["content", "content_and_artifact"] = "content_and_artifact"

    base_url: str = "https://api.open-meteo.com/v1/"
    forcast_url: str = urljoin(base_url, "forecast")
    geocoding_url: str = "https://geocoding-api.open-meteo.com/v1/search/"
    apikey: str | None = None

    session: CachedSession = CachedSession(
        "openmeteo.cache", expire_after=-1, ignored_parameters=["apikey"]
    )
    """Synchronous requests session with cache support."""

    @model_validator(mode="after")
    def patch_request_timeout(self) -> Self:
        # Monkey patch the session to add a global timeout
        self.session.request = functools.partial(self.session.request, timeout=5)
        return self

    def _run(
        self,
        location: str,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> tuple[dict, dict]:
        geocoding = self._get_geocoding(location)
        params = (
            geocoding._asdict()
            | {
                "timezone": "auto",
            }
            | kwargs
        )

        if self.apikey:
            params["apikey"] = self.apikey

        try:
            data = self._forcast(params)
        except HTTPError as http_err:
            raise ToolException(str(http_err))
        else:
            data = self._format_response(data)
            return data, {"url": f"{self.forcast_url}?{urlencode(params)}"}

    @retry(
        retry=retry_if_exception_type((HTTPError, Timeout)), stop=stop_after_attempt(3)
    )
    def _get_geocoding(self, location: str) -> GeoCoding:
        """
        See <https://open-meteo.com/en/docs/geocoding-api>
        """
        params = {"name": location, "count": 1}
        if self.apikey:
            params["apikey"] = self.apikey

        response = self.session.get(self.geocoding_url, params=params)
        # Should not happen. Wrong location will result in an empty list.
        response.raise_for_status()
        data = response.json()
        if "results" not in data:
            raise ToolException("Invalid location")
        target = ["results"][0]
        return GeoCoding(latitude=target["latitude"], longitude=target["longitude"])

    @retry(
        retry=retry_if_exception_type((HTTPError, Timeout)), stop=stop_after_attempt(3)
    )
    def _forcast(self, params: dict) -> dict:
        """A request wrapper. Mainly for retrying."""
        response = self.session.get(self.forcast_url, params=params)
        response.raise_for_status()
        return response.json()

    async def _arun(
        self,
        location: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> tuple[dict, dict]:
        geocoding = await self._aget_geocoding(location)
        params = (
            geocoding._asdict()
            | {
                "timezone": "auto",
            }
            | kwargs
        )

        if self.apikey:
            params["apikey"] = self.apikey

        try:
            data = await self._aforcast(params)
        except ClientResponseError as http_err:
            raise ToolException(str(http_err))
        else:
            data = self._format_response(data)
            return data, {"url": f"{self.forcast_url}?{urlencode(params)}"}

    @retry(
        retry=retry_if_exception_type((ClientResponseError, TimeoutError)),
        stop=stop_after_attempt(3),
    )
    async def _aforcast(self, params: dict) -> dict:
        """A request wrapper. Mainly for retrying."""
        # TODO: The timeout is a bit complicated for aiohttp, using default for now.
        async with AsyncCachedSession(
            cache=SQLiteBackend("openmeteo.async.cache"), raise_for_status=True
        ) as session:
            async with await session.get(self.forcast_url, params=params) as response:
                return await response.json()

    @retry(
        retry=retry_if_exception_type((ClientResponseError, TimeoutError)),
        stop=stop_after_attempt(3),
    )
    async def _aget_geocoding(self, location: str) -> GeoCoding:
        """
        See <https://open-meteo.com/en/docs/geocoding-api>
        """
        params = {"name": location, "count": 1}
        if self.apikey:
            params["apikey"] = self.apikey

        # The `raise_for_status` should not happen. Wrong location will result in an empty list.
        # TODO: The timeout is a bit complicated for aiohttp, using default for now.
        async with AsyncCachedSession(
            cache=SQLiteBackend("openmeteo.async.cache"), raise_for_status=True
        ) as session:
            async with await session.get(self.geocoding_url, params=params) as response:
                data = await response.json()
                if "results" not in data:
                    raise ToolException("Invalid location")
                target = data["results"][0]
                return GeoCoding(
                    latitude=target["latitude"], longitude=target["longitude"]
                )

    def _format_response(self, data: dict) -> dict:
        """Formats a response containing daily and hourly data.

        This function extracts daily and hourly data from the input data and restructures it
        using the corresponding unit information.

        Args:
            data: A dictionary containing daily and hourly data, along with their unit information.

        Returns:
            A dictionary containing the restructured daily and hourly data.

        Raises:
            ValueError: If daily or hourly data is present but the corresponding unit information is missing.
        """
        formatted_data = {}

        for period in ["daily", "hourly"]:
            period_data = data.get(period)
            period_units = data.get(f"{period}_units")

            if period_data is not None:
                if period_units is not None:
                    formatted_data[period] = self._restructure_ts_data(
                        period_data, period_units
                    )
                else:
                    raise ValueError(f"Missing units for {period} data.")
        if (current := data.get("current")) is not None:
            current_units = data.get("current_units")
            if current_units is not None:
                formatted_data["current"] = self._restructure_data(
                    current, current_units
                )
            else:
                raise ValueError("Missing units for current data.")

        return formatted_data

    def _restructure_data(self, data_values: dict, data_units: dict) -> dict:
        """Restructures data, associating data values with their unit information.

        This function restructures data (e.g., 'current' data) into a dictionary
        keyed by time, where value contains the corresponding data with unit information.

        Args:
            data_values: A dictionary containing the data.
            data_units: A dictionary containing the unit information for the data.

        Returns:
            A dictionary containing the restructured data.
        """
        time_as_key = data_values["time"]
        restructured_data = {time_as_key: {}}

        for data_key, value in data_values.items():
            if data_key in {"time", "interval"}:
                continue

            if data_key == "weather_code":
                # For weather code, I patch the description in the response so that LLMs can have a better understanding of the meaning.
                desc = wmo_description.get(value)
                if not desc:
                    logger.warning(
                        "Unknown wmo code: %s. Consider change reference to <https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM>",
                        value,
                    )
                restructured_data[time_as_key][data_key] = (
                    f"{value} - {desc}" if desc else value
                )
            else:
                unit = data_units.get(data_key, "")
                formatted_key = f"{data_key} ({unit})" if unit else data_key
                restructured_data[time_as_key][formatted_key] = value

        return restructured_data

    def _restructure_ts_data(self, data_values: dict, data_units: dict) -> dict:
        """Restructures time-series data, associating data values with their unit information.

        This function restructures time-series data (e.g., daily or hourly data) into a dictionary
        keyed by time, where each time point's value contains the corresponding data with unit information.

        Args:
            data_values: A dictionary containing the time-series data.
            data_units: A dictionary containing the unit information for the data.

        Returns:
            A dictionary containing the restructured time-series data.
        """
        time_series = data_values["time"]
        restructured_data = {time: {} for time in time_series}

        for data_key, values in data_values.items():
            if data_key == "time":
                continue

            if data_key == "weather_code":
                # For weather code, I patch the description in the response so that LLMs can have a better understanding of the meaning.
                for index, value in enumerate(values):
                    desc = wmo_description.get(value)
                    if not desc:
                        logger.warning(
                            "Unknown wmo code: %s. Consider change reference to <https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM>",
                            value,
                        )
                    time_as_key = time_series[index]
                    restructured_data[time_as_key][data_key] = (
                        f"{value} - {desc}" if desc else value
                    )

            unit = data_units.get(data_key, "")
            formatted_key = f"{data_key} ({unit})" if unit else data_key

            for index, value in enumerate(values):
                time_as_key = time_series[index]
                restructured_data[time_as_key][formatted_key] = value

        return restructured_data

    def __del__(self):
        """cleanup"""
        self.session.close()
