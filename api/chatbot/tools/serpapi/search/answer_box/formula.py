from typing import Any, Literal

from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel


class Parameter(ExcludeNoneModel):
    symbol: str
    name: str
    value: float | int | Any
    unit: str


class FormulaAnswerBox(BaseAnswerBox):
    """SerperApi formula answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-formula-answer-box>
    """

    type: Literal["formula"]
    title: str
    solve_for: str
    solve_for_alternatives: list[str]
    answer: str
    solutions: list[str]
    answer_alternatives: list[str]
    parameters: list[Parameter]

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {
            "solve_for_alternatives",
            "answer_alternatives",
            "parameters",
        },
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {
            "solve_for_alternatives",
            "answer_alternatives",
            "parameters",
        },
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
