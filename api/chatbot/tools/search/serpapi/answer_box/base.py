from abc import ABC
from typing import Any

from pydantic import BaseModel, HttpUrl


class ExcludeNoneModel(BaseModel):
    """Base model to exclude None values when dumping."""

    def model_dump(self, *, exclude_none: bool = True, **kwargs) -> dict[str, Any]:
        return super().model_dump(exclude_none=exclude_none, **kwargs)

    def model_dump_json(self, *, exclude_none: bool = True, **kwargs) -> str:
        return super().model_dump_json(exclude_none=exclude_none, **kwargs)


class BaseAnswerBox(ExcludeNoneModel, ABC):
    type: str


class Source(ExcludeNoneModel):
    name: str | None = None
    title: str | None = None
    link: HttpUrl
    logo: HttpUrl | None = None


class TableItem(ExcludeNoneModel):
    name: str
    value: str | float
