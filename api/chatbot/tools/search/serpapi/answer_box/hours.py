from typing import Any, Literal

from pydantic import HttpUrl
from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel


class LocalHoursResult(ExcludeNoneModel):
    title: str
    link: HttpUrl
    serpapi_link: HttpUrl


# TODO: WIP
class HoursAnswerBox(BaseAnswerBox):
    """SerperApi open hours answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-open-hours-answer-box>
    """

    type: Literal["hours"]
    description: str
    result: str
    local_hours_results: list[LocalHoursResult] | None = None

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"local_hours_results"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"local_hours_results"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
