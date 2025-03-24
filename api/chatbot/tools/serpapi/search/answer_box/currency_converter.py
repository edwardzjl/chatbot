from typing import Any, Literal

from pydantic import ConfigDict, Field
from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel


class Currency(ExcludeNoneModel):
    price: float | int
    currency: str


class CurrencyConverter(ExcludeNoneModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: Currency = Field(alias="from")
    to: Currency


class ChartPoint(ExcludeNoneModel):
    price: float | int
    time: str
    unix_time: int


class CurrencyConverterAnswerBox(BaseAnswerBox):
    """SerperApi currency converter answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-converter-answer-box>
    """

    type: Literal["currency_converter"]
    result: str
    price: float
    currency: str
    date: str
    currency_converter: CurrencyConverter
    chart: list[ChartPoint]

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"chart"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"chart"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
