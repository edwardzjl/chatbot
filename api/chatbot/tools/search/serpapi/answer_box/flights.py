from typing import Any, Literal

from pydantic import ConfigDict, HttpUrl, Field
from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel


class Flight(ExcludeNoneModel):
    link: HttpUrl
    flight_info: list[str]


class FlightFrom(ExcludeNoneModel):
    departing_place: str
    departing_airport: str


class FlightTo(ExcludeNoneModel):
    arriving_place: str
    arriving_airport: str


class SearchInformation(ExcludeNoneModel):
    model_config = ConfigDict(populate_by_name=True)

    trip_type: str
    booking_class: str
    from_: FlightFrom = Field(alias="from")
    to: FlightTo


class OtherFlight(ExcludeNoneModel):
    departure_date: str
    return_date: str
    price: str
    percentage_of_highest_price: float
    booking_class: str


class FlightsAnswerBox(BaseAnswerBox):
    """SerperApi flights answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-flights-answer-box>
    """

    type: Literal["google_flights"]
    title: str
    flights: list[Flight]
    link: HttpUrl
    search_information: SearchInformation
    cheapest_flights: list[OtherFlight]

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"search_information", "cheapest_flights"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"search_information", "cheapest_flights"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
