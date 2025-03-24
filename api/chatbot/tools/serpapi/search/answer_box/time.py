from typing import Literal

from .base import BaseAnswerBox


class TimeAnswerBox(BaseAnswerBox):
    """SerperApi sunrise / sunset time answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-sunrise-sunset-time-answer-box>
    """

    type: Literal["time"]
    result: str
    date: str
    description: str
