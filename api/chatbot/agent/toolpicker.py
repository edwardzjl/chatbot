from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, TypeAlias

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


def create_tool_picker(chat_model: BaseChatModel, tools: list[BaseTool]) -> Runnable:
    assert tools, "No tools provided to the tool picker."

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

    instruction = """You are a helpful assistant with access to a set of tools. Use them only when truly necessary.

Now, choose the most appropriate tool(s) to proceed with your response.
"""

    tmpl = ChatPromptTemplate.from_messages(
        [
            ("system", instruction),
            ("placeholder", "{messages}"),
        ]
    )

    # Disable thinking for reasoning models.
    # NOTE: this may only work for VLLM.
    extra_body = chat_model.extra_body | {
        "chat_template_kwargs": {"enable_thinking": False}
    }

    return tmpl | chat_model.with_structured_output(
        PickTools,
        method="json_schema",
        strict=True,
        include_raw=True,
        tools=[PickTools],
    ).bind(extra_body=extra_body).with_config(tags=["internal"])
