from typing import Literal

from pydantic import ConfigDict, Field

from .base import BaseAnswerBox


# TODO: WIP
class TransportOptionsAnswerBox(BaseAnswerBox):
    """SerperApi transport options answer box schema.

    See <https://serpapi.com/direct-answer-box-api#api-examples-transport-options-answer-box>
    """

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["transport_options"]
    title: str
    from_: str = Field(alias="from")
    to: str
    date: str
    time: str
    climate_friendly: bool
