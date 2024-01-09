from typing import Any, Literal

from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import ChatPromptTemplate

from chatbot.prompts.base import FlexPromptValue

# TODO: this section is mainly used for formatting history messages or agent scratchpads.
# As Literal cannot use variables, this lead to a bit of duplication.
HUMAN_PREFIX = "<s> ### User:\n"
HUMAN_SUFFIX = "\n"
AI_PREFIX = "### Assistant:\n"
AI_SUFFIX = "</s>"


class SolarPromptTemplate(ChatPromptTemplate):
    """A prompt template for Solar models.
    See <https://huggingface.co/upstage/SOLAR-10.7B-Instruct-v1.0#conducting-single-turn-conversation>.
    The system message format was inspired by user message format.
    """

    def format_prompt(self, **kwargs: Any) -> PromptValue:
        """Format prompt."""
        messages = self.format_messages(**kwargs)
        return SolarPromptValue(messages=messages)


class SolarPromptValue(FlexPromptValue):
    """Solar prompt value."""

    system_prefix: Literal["<s> ### System:\n"] = "<s> ### System:\n"
    system_suffix: Literal["</s>"] = "</s>"
    human_prefix: Literal["<s> ### User:\n"] = "<s> ### User:\n"
    human_suffix: Literal["\n"] = "\n"
    ai_prefix: Literal["### Assistant:\n"] = "### Assistant:\n"
    ai_suffix: Literal["</s>"] = "</s>"
