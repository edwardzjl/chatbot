from typing import Any, Literal

from pydantic import HttpUrl
from pydantic.main import IncEx

from .base import BaseAnswerBox, ExcludeNoneModel, Source


class ExpandedListItem(ExcludeNoneModel):
    title: str
    thumbnail: HttpUrl

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


class ExpandedListAnswerBox(BaseAnswerBox):
    """SerperApi expanded list answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-expanded-list-answer-box>
    """

    type: Literal["organic_result"]
    expanded_list: list[ExpandedListItem]


class OrganicContents(ExcludeNoneModel):
    table: list[list[str]]


class OrganicResultAnswerBox(BaseAnswerBox, Source):
    """SerperApi organic result answer box type 1 schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-organic-result-answer-box-type-1>
    and <https://serpapi.com/direct-answer-box-api#api-examples-organic-result-answer-box-type-6>
    """

    type: Literal["organic_result"]
    displayed_link: str
    date: str | None = None
    snippet: str | None = None
    snippet_highlighted_words: list[str] | None = None
    answer: str | None = None
    """Exists in example 6."""
    favicon: HttpUrl | None = None
    source: str | None = None
    thumbnail: HttpUrl | None = None
    contents: OrganicContents | None = None
    """Search for 'Sunset in Hangzhou'."""

    def model_dump(
        self,
        *,
        exclude: IncEx | None = {"displayed_link", "favicon", "source", "thumbnail"},
        **kwargs,
    ) -> dict[str, Any]:
        return super().model_dump(exclude=exclude, **kwargs)

    def model_dump_json(
        self,
        *,
        exclude: IncEx | None = {"displayed_link", "favicon", "source", "thumbnail"},
        **kwargs,
    ) -> str:
        return super().model_dump_json(exclude=exclude, **kwargs)
