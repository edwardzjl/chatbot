from typing import Literal

from .base import BaseAnswerBox


class FlightDurationAnswerBox(BaseAnswerBox):
    """SerperApi flight duration answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-flight-duration-answer-box>
    """

    type: Literal["flight_duration"]
    duration: str
    stops: str
    direction: str
