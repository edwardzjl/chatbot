import json
import logging
from typing import TypeAlias

from pydantic import BaseModel

from .answerbox import (
    OrganicAnswerBox,
    WeatherAnswerBox,
    FlightDurationAnswerBox,
    CalculatorResultAnswerBox,
    PopulationAnswerBox,
)
from .organic_result import OrganicResult


logger = logging.getLogger(__name__)


AnswerBoxType: TypeAlias = (
    OrganicAnswerBox
    | WeatherAnswerBox
    | FlightDurationAnswerBox
    | CalculatorResultAnswerBox
    | PopulationAnswerBox
)


class SearchResult(BaseModel):
    # TODO: The `answer_box` field is almost unusable now.
    # You can check <https://serpapi.com/google-light-answer-box> and try it yourself.
    # It wastes me tens of search requests.
    # answer_box: AnswerBoxType | None = Field(discriminator="type", default=None)
    organic_results: list[OrganicResult] | None = None

    def dump_minimal(self) -> str:
        # if self.answer_box:
        #     return self.answer_box.model_dump_json()
        res = [
            organic_result.model_dump(include={"title", "snippet", "link"})
            for organic_result in self.organic_results
        ]
        return json.dumps(res, ensure_ascii=False)
