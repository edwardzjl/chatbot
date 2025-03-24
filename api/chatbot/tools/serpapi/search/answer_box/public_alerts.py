from typing import Literal

from pydantic import HttpUrl

from .base import BaseAnswerBox, ExcludeNoneModel, Source


class PublicAlert(ExcludeNoneModel, Source):
    details: str
    date: str


# TODO: WIP
class PublicAlertsAnswerBox(BaseAnswerBox):
    """SerperApi public alerts answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-public-alerts-answer-box-type-1>
    and <https://serpapi.com/direct-answer-box-api#api-examples-public-alerts-answer-box-type-2>
    """

    type: Literal["public_alerts"]
    result: str
    disclaimer: str
    alerts: list[PublicAlert]
    details: list[str] | None = None
    additional_info: list[str] | None = None
