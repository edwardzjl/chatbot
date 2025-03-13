from typing import Any, Literal

from pydantic import HttpUrl
from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel, Source


class HotelQuery(ExcludeNoneModel):
    location: str
    days: list[str]
    people: int


class HotelInfo(ExcludeNoneModel, Source):
    image: HttpUrl
    price: str
    rating: float
    reviews: int
    deal: str
    sale: str
    features: list[str] | None = None

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"image", "deal", "sale"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"image", "deal", "sale"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)


class MapResult(ExcludeNoneModel):
    price: str
    latitude: float
    longitude: float


class HotelsAnswerBox(BaseAnswerBox):
    """SerperApi hotels answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-hotels-answer-box>
    """

    type: Literal["hotels"]
    query: HotelQuery
    hotels: list[HotelInfo]
    map_results: list[MapResult]

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"query", "map_results"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"query", "map_results"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
