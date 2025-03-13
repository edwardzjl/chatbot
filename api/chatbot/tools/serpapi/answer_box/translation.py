from typing import Literal

from .base import BaseAnswerBox, ExcludeNoneModel


class Words(ExcludeNoneModel):
    language: str
    text: str
    pronunciation: str | None = None


class Translation(ExcludeNoneModel):
    source: Words
    target: Words


class Interjection(ExcludeNoneModel):
    title: str
    value: list[str]


class TranslationAnswerBox(BaseAnswerBox):
    """SerperApi translation answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-translation-answer-box>
    """

    type: Literal["translation_result"]
    translation: Translation
    interjection: Interjection
