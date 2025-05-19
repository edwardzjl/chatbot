from __future__ import annotations

import logging
from datetime import datetime, UTC
from typing import TYPE_CHECKING, Annotated, Callable, Literal, TypeAlias

from langchain_core.messages import BaseMessage, SystemMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from chatbot.safety import create_hazard_classifier, hazard_categories

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.graph.graph import CompiledGraph


logger = logging.getLogger(__name__)


def create_agent(
    chat_model: BaseChatModel,
    *,
    safety_model: BaseChatModel | None = None,
    checkpointer: BaseCheckpointSaver = None,
    token_counter: (
        Callable[[list[BaseMessage]], int] | Callable[[BaseMessage], int] | None
    ) = None,
    context_length: int | None = None,
    tools: list[BaseTool] = None,
) -> CompiledGraph:
    if token_counter is None:
        if hasattr(chat_model, "get_num_tokens_from_messages"):
            token_counter = chat_model.get_num_tokens_from_messages
        else:
            logger.warning(
                "Could not get token counter function from chat model, will truncate messages by message count. This may lead to context overflow."
            )
            token_counter = len

    if context_length is None:
        try:
            context_length = chat_model.get_context_length()
        except AttributeError:
            logger.warning(
                "Could not get context length from chat model, meanwhile not providing one."
            )
            context_length = 20

    # TODO: need to consider if `token_counter` is len.
    try:
        # `ChatOpenAI.max_tokens` is actually `max_completion_tokens` i.e. Maximum number of tokens to generate.
        max_input_tokens = context_length - chat_model.max_tokens
    except AttributeError:
        # Otherwise, leave 0.2 for new tokens
        max_input_tokens = int(context_length * 0.8)
    except TypeError:
        max_input_tokens = int(context_length * 0.8)

    tool_picker = create_tool_picker(chat_model, tools) if tools else None
    tool_node = ToolNode(tools) if tools else None

    hazard_classifier = None
    if safety_model is not None:
        hazard_classifier = create_hazard_classifier(safety_model)

    async def input_guard(state: MessagesState) -> MessagesState:
        if hazard_classifier is not None:
            last_message = state["messages"][-1]
            flag, category = await hazard_classifier.ainvoke(
                input={"messages": [last_message]}
            )
            if flag == "unsafe" and category is not None:
                return {
                    "messages": [
                        SystemMessage(
                            content=[
                                {
                                    "type": "guard_content",
                                    "guard_content": {
                                        "category": category,
                                        "text": f"""The user input may contain inproper content related to:
{hazard_categories.get(category)}

Please respond with care and professionalism. Avoid engaging with harmful or unethical content. Instead, guide the user towards more constructive and respectful communication.""",
                                    },
                                }
                            ]
                        )
                    ]
                }
        return {"messages": []}

    async def run_output_guard(state: MessagesState) -> MessagesState:
        if hazard_classifier is not None:
            flag, category = await hazard_classifier.ainvoke(
                input={"messages": state["messages"][-2:]}
            )
            if flag == "unsafe" and category is not None:
                # TODO: implementation
                # Re-generate? or how can I update the last message?
                ...
        return {"messages": []}

    async def chatbot(state: MessagesState, config: RunnableConfig) -> MessagesState:
        """Process the current state and generate a response using the LLM."""

        instruction = """You are Rei, the ideal assistant dedicated to assisting users effectively. Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity.

When solving problems, decompose them into smaller parts, think through each part step by step before providing your final answer. Enclose your thought process within XML tags: <think> and </think>.
The content inside the <think> tags is for your internal use only and will not be visible to the user or me.

Current date: {date}
"""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", instruction),
                ("placeholder", "{messages}"),
            ]
        )

        windowed_messages: list[BaseMessage] = trim_messages(
            state["messages"],
            token_counter=token_counter,
            max_tokens=max_input_tokens,
            start_on="human",  # This means that the first message should be from the user after trimming.
        )

        if tool_picker:
            try:
                tool_names_out = await tool_picker.ainvoke(
                    input={"messages": windowed_messages}
                )
                tool_names = tool_names_out["parsed"].tool_names
                selected_tools = (
                    [tool for tool in tools if tool.name in tool_names]
                    if tool_names
                    else []
                )

                if selected_tools:
                    bound = prompt | chat_model.bind_tools(selected_tools)
                else:
                    bound = prompt | chat_model
            except Exception:
                logger.exception("Error picking tools, binding all")
                bound = prompt | chat_model.bind_tools(tools)

        last_message_at = windowed_messages[-1].additional_kwargs.get("sent_at")
        responding_at = (
            datetime.fromisoformat(last_message_at)
            if last_message_at
            else datetime.now(tz=UTC)
        )

        messages = await bound.ainvoke(
            {
                "messages": windowed_messages,
                "date": responding_at.strftime("%Y-%m-%d (%A)"),
            }
        )
        return {"messages": [messages]}

    # I cannot use `END` as the literal hint, as:
    #  > Type arguments for "Literal" must be None, a literal value (int, bool, str, or bytes), or an enum value.
    # As `END` is just an intern string of "__end__" (See `langgraph.constants`), So I use "__end__" here.
    def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    builder = StateGraph(MessagesState)
    builder.add_node(input_guard)
    builder.add_node(chatbot)
    builder.add_edge(START, "input_guard")
    builder.add_edge("input_guard", "chatbot")
    if tool_node:
        builder.add_node(tool_node)
        builder.add_conditional_edges("chatbot", should_continue)
        builder.add_edge("tools", "chatbot")
    else:
        builder.add_edge("chatbot", END)

    return builder.compile(checkpointer=checkpointer)


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

    instruction = """You are a helpful assistant. You have access to tools, but should only use them when necessary.

Your primary task is to select the appropriate tools for the user's query by calling the `PickTools` function. You MUST always call `PickTools` as your first step to determine if any tools are needed.
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
