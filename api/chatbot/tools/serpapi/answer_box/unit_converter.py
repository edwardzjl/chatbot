from typing import Literal

from pydantic import ConfigDict, Field

from .base import BaseAnswerBox, ExcludeNoneModel


class Observation(ExcludeNoneModel):
    value: float | int
    unit: str


class UnitConverterAnswerBox(BaseAnswerBox):
    """SerperApi unit converter answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-unit-converter-answer-box>
    """

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["unit_converter"]
    unit_type: str
    from_: Observation = Field(alias="from")
    to: Observation
    formula: str
