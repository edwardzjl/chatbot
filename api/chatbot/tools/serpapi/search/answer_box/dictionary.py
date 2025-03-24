from typing import Any, Literal

from pydantic import HttpUrl
from pydantic.main import IncEx

from .base import BaseAnswerBox


class DictionaryAnswerBox(BaseAnswerBox):
    """SerperApi dictionary answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-dictionary-answer-box>
    """

    type: Literal["dictionary_results"]
    syllables: str
    pronunciation_audio: HttpUrl
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
