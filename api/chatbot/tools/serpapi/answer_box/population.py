from typing import Any, Literal

from pydantic import HttpUrl
from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel


class PopulationOverview(ExcludeNoneModel):
    place: str
    population: str


class Source(ExcludeNoneModel):
    name: str
    link: HttpUrl


class PopulationAnswerBox(BaseAnswerBox):
    """SerperApi population answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-population-answer-box>
    """

    type: Literal["population_result"]
    population: str
    year: str
    other: list[PopulationOverview]
    sources: list[Source]

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {
            "other",
            "sources",
        },
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {
            "other",
            "sources",
        },
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
