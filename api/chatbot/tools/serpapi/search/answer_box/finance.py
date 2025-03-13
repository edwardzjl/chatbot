from typing import Any, Literal

from pydantic import HttpUrl
from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel, TableItem


class PriceMovement(ExcludeNoneModel):
    price: float
    percentage: float
    movement: str
    date: str | None = None


class Market(ExcludeNoneModel):
    closed: bool
    date: str
    trading: str
    price: float
    price_movement: PriceMovement


class FinanceAnswerBox(BaseAnswerBox):
    """SerperApi finance answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-finance-answer-box>
    """

    type: Literal["finance_results"]
    title: str
    exchange: str
    stock: str
    currency: str
    price: float
    thumbnail: HttpUrl
    price_movement: PriceMovement
    market: Market
    previous_close: float
    table: list[TableItem]

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"thumbnail"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"thumbnail"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
