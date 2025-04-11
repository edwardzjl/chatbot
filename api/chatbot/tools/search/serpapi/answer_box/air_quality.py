from typing import Any, Literal

from pydantic import HttpUrl
from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel, Source


class Index(ExcludeNoneModel):
    hex_color: str
    name: str
    extracted_min: int
    extracted_max: int | None = None
    extracted_name: str


class AqiBasics(ExcludeNoneModel):
    source: str
    source_link: HttpUrl
    index_reference: str
    index_reference_link: HttpUrl
    indexes: list[Index]
    snippets: list[str]
    learn_more_link: HttpUrl


class Pollutant(ExcludeNoneModel):
    pollutant: str
    category: str


class AirQualityStation(ExcludeNoneModel):
    name: str
    location: str
    aqi_value: int
    aqi_status: str
    remark: str
    provider: str
    time: str


class SelectedAirQualityStation(AirQualityStation):
    aqi_hex_color: str
    table: list[Pollutant]


# TODO: WIP
class AirQualityAnswerBox(BaseAnswerBox):
    """SerperApi air quality answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-air-quality-answer-box>
    """

    type: Literal["air_quality"]
    sources: list[Source]
    map_link: HttpUrl
    aqi_basics: AqiBasics
    stations: list[SelectedAirQualityStation]
    full_stations_table: list[AirQualityStation]

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"map_link", "aqi_basics", "full_stations_table"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"map_link", "aqi_basics", "full_stations_table"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
