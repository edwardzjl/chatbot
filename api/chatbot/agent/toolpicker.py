from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Callable, Literal, TypeAlias

from langchain_core.messages import BaseMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from .token_management import resolve_token_management_params

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


SYS_INST = """You are a helpful assistant with access to a set of tools. Use them only when truly necessary.

Now, choose the most appropriate tool(s) to proceed with your response.
"""


def create_tool_picker(
    chat_model: BaseChatModel,
    tools: list[BaseTool],
    *,
    token_counter: Callable[[list[BaseMessage]], int]
    | Callable[[BaseMessage], int]
    | None = None,
    context_length: int | None = None,
) -> Runnable:
    assert tools, "No tools provided to the tool picker."

    token_counter, max_input_tokens, _ = resolve_token_management_params(
        chat_model, token_counter, context_length
    )

    tool_names = [tool.name for tool in tools]
    ToolNamesType: TypeAlias = set[Literal[*tool_names]] | None  # type: ignore

    valid_options = [
        "- `None`: No tool needed. You can answer based on your existing knowledge, or the task does not require fetching external information."
    ] + [f"- `{tool.name}`: {tool.description}" for tool in tools]

    class PickTools(BaseModel):
        """Use this tool to pick the right tools."""

        tool_names: Annotated[
            ToolNamesType,
            Field(
                description=f"A set of tools required for the task. Can be `None` if no tools are needed. Valid options:\n{'\n'.join(valid_options)}"
            ),
        ]

    tmpl = ChatPromptTemplate.from_messages(
        [
            ("system", SYS_INST),
            ("placeholder", "{messages}"),
        ]
    )

    # Notice we don't pass in messages. This creates
    # a RunnableLambda that takes messages as input
    trimmer = trim_messages(
        token_counter=token_counter,
        max_tokens=max_input_tokens,
        start_on="human",
        include_system=True,
    )

    # Disable thinking for reasoning models.
    # NOTE: this may only work for VLLM.
    extra_body = chat_model.extra_body or {}
    extra_body = extra_body | {"chat_template_kwargs": {"enable_thinking": False}}

    return (
        tmpl
        | trimmer
        | chat_model.with_structured_output(
            PickTools,
            method="json_schema",
            strict=True,
            include_raw=True,
            tools=[PickTools],
        )
        .bind(extra_body=extra_body)
        .with_config(tags=["internal"])
    )
