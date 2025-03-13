from typing import Any, Literal

from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel, Source


# TODO: the names are a mess


class MathExpression(ExcludeNoneModel):
    expression: str
    annotation: str


class MathDescription(ExcludeNoneModel):
    description: str
    steps: list[MathExpression] | None = None


class SolutionStep(ExcludeNoneModel):
    number: int
    description: str
    details: list[MathExpression | MathDescription]
    answer: MathExpression


class MathSolution(ExcludeNoneModel):
    name: str
    steps: list[SolutionStep]


# TODO: WIP
class MathSolutionAnswerBox(BaseAnswerBox):
    """SerperApi math solution answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-math-solution-answer-box>
    """

    type: Literal["math_solution"]
    problem: MathExpression
    solutions: list[MathSolution]
    answer: MathExpression
    answer_in_alternative_form: MathExpression
    solutions_on_the_web: list[Source]

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"solutions_on_the_web"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"solutions_on_the_web"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
