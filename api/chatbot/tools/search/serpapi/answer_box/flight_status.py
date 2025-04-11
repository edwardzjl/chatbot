from typing import Literal

from .base import BaseAnswerBox, ExcludeNoneModel, Source


class Waypoint(ExcludeNoneModel):
    airport_name: str
    planned_time: str
    actual_time: str
    terminal: str
    gate: str
    location: str
    date: str


# TODO: WIP
class FlightStatusAnswerBox(BaseAnswerBox):
    """SerperApi flight status answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-flight-status-answer-box>
    """

    type: Literal["flight_status"]
    title: str
    destination: str
    flight_number: str
    flight_status: str
    latest_update: str
    percentage_of_flight_progress: int
    sources: list[Source]
    departure: Waypoint
    arrival: Waypoint
