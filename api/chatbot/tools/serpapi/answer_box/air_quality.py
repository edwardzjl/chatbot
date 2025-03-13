from typing import Any, Literal

from pydantic import HttpUrl
from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel


class AirQualitySource(ExcludeNoneModel):
    title: str
    link: HttpUrl


class Pollutant(ExcludeNoneModel):
    pollutant: str
    category: str


class AirQualityStation(ExcludeNoneModel):
    ...


# TODO: WIP
class AirQualityAnswerBox(BaseAnswerBox):
    """SerperApi air quality answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-air-quality-answer-box>
    """
    type: Literal["air_quality"]
    sources: list[AirQualitySource]
    map_link: HttpUrl

    def model_dump(
        self, *, exclude: IncEx | None = {"map_link"}, **kwargs
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self, *, exclude: IncEx | None = {"map_link"}, **kwargs
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
