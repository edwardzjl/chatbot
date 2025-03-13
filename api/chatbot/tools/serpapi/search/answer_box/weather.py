from abc import ABC
from typing import Any, Literal

from pydantic import HttpUrl
from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel, Source


class Temperature(ExcludeNoneModel):
    high: int | float  # maybe it's str?
    low: int | float  # maybe it's str?


class BaseWeatherForcast(ExcludeNoneModel, ABC):
    temperature: Temperature
    thumbnail: HttpUrl
    weather: str
    humidity: str
    precipitation: str
    wind: str

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"thumbnail"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"thumbnail"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)


class DailyForcast(BaseWeatherForcast):
    day: str


class HourlyForcast(BaseWeatherForcast):
    time: str


class PrecipitationForecast(ExcludeNoneModel):
    precipitation: str
    day: str
    time: str


class WindForcast(ExcludeNoneModel):
    angle: int
    direction: str
    speed: str
    time: str


class WeatherAnswerBox(BaseAnswerBox):
    """SerperApi weather answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-weather-answer-box>
    """

    type: Literal["weather_result"]
    temperature: int | float  # maybe it's str?
    unit: str
    precipitation: str
    humidity: str
    wind: str
    location: str
    date: str
    weather: str
    thumbnail: HttpUrl
    forecast: list[DailyForcast]
    hourly_forecast: list[HourlyForcast]
    precipitation_forecast: list[PrecipitationForecast]
    wind_forecast: list[WindForcast]
    sources: list[Source]

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {
            "hourly_forecast",
            "precipitation_forecast",
            "wind_forecast",
        },
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {
            "hourly_forecast",
            "precipitation_forecast",
            "wind_forecast",
        },
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
