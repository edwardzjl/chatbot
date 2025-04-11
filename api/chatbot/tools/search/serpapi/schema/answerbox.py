from typing import Any, Literal

from pydantic import Field
from pydantic.main import IncEx

from .base import ExcludeNoneModel


class OrganicAnswerBox(ExcludeNoneModel):
    """Organic Answer Box.

    - <https://serpapi.com/google-light-answer-box#api-examples-organic-answer-box-type-1>
    - <https://serpapi.com/google-light-answer-box#api-examples-organic-answer-box-type-2>
    - <https://serpapi.com/google-light-answer-box#api-examples-organic-answer-box-type-3>
    - <https://serpapi.com/google-light-answer-box#api-examples-organic-answer-box-type-4>
    """

    type: Literal["organic_result"] = "organic_result"
    title: str
    # Consider HttpUrl?
    link: str | None = None
    displayed_link: str | None = None
    snippet: str | None = None
    snippet_highlighted_words: list[str] | None = None
    _list: list[str] | None = Field(alias="list", default=None)
    # Consider HttpUrl?
    thumbnail: str | None = None
    answer: str | None = None

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"link", "displayed_link", "thumbnail"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"link", "displayed_link", "thumbnail"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)


class TimeAnswerBox(ExcludeNoneModel):
    """Time Answer Box.

    <https://serpapi.com/google-light-answer-box#api-examples-time-answer-box>
    """

    type: Literal["time"] = "time"
    result: str
    date: str
    description: str
    location: str


class WeatherAlert(ExcludeNoneModel):
    type: str
    source: str


class WeatherAnswerBox(ExcludeNoneModel):
    """Weather Answer Box.

    - <https://serpapi.com/google-light-answer-box#api-examples-weather-answer-box>
    - <https://serpapi.com/google-light-answer-box#api-examples-weather-answer-box-with-alert>
    """

    type: Literal["weather_result"] = "weather_result"
    temperature: str
    unit: str
    high: str | None = None
    low: str | None = None
    weather: str
    date: str
    location: str
    # Consider HttpUrl?
    source: str | None = None
    # Consider HttpUrl?
    icon: str
    alert: list[WeatherAlert] | None = None

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"source", "icon"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"source", "icon"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)


class DictionaryAnswerBox(ExcludeNoneModel):
    """Dictionary Answer Box.

    <https://serpapi.com/google-light-answer-box#api-examples-dictionary-answer-box>
    """

    type: Literal["dictionary_results"] = "dictionary_results"
    syllables: str
    # Consider HttpUrl?
    pronunciation_audio: str
    phonetic: str
    word_type: str
    definitions: list[str]
    examples: list[str]
    extras: list[str]

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"pronunciation_audio", "extras"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"pronunciation_audio", "extras"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)


class FlightDurationAnswerBox(ExcludeNoneModel):
    """Flight Duration Answer Box.

    <https://serpapi.com/google-light-answer-box#api-examples-flight-duration-answer-box>
    """

    type: Literal["flight_duration"] = "flight_duration"
    duration: str
    stops: str
    details: str


class CalculatorResultAnswerBox(ExcludeNoneModel):
    """Calculator Result Answer Box.

    <https://serpapi.com/google-light-answer-box#api-examples-calculator-result-answer-box>
    """

    type: Literal["calculator_result"] = "calculator_result"
    problem: str
    result: str


class PopulationAnswerBox(ExcludeNoneModel):
    """Population Answer Box.

    <https://serpapi.com/google-light-answer-box#api-examples-population-answer-box>
    """

    type: Literal["population_result"] = "population_result"
    place: str
    population: str
    year: str
    source: str
    # Consider HttpUrl?
    source_link: str

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"source_link"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"source_link"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
