from __future__ import annotations

import logging
from datetime import datetime, UTC
from typing import TYPE_CHECKING, Any, Callable

from langchain_core.messages import BaseMessage, SystemMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from chatbot.safety import create_hazard_classifier, hazard_categories

from .token_management import resolve_token_management_params
from .toolpicker import create_tool_picker

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.graph.state import CompiledStateGraph


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
) -> CompiledStateGraph:
    token_counter, max_input_tokens, _ = resolve_token_management_params(
        chat_model, token_counter, context_length
    )

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
                message = SystemMessage(
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
                return {"messages": [message]}
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

        # Notice we don't pass in messages. This creates
        # a RunnableLambda that takes messages as input
        trimmer = trim_messages(
            token_counter=token_counter,
            max_tokens=max_input_tokens,
            start_on="human",
            include_system=True,
        )

        bound = RunnablePassthrough.assign(date=_get_responding_at) | prompt | trimmer

        selected_tools = []
        if tool_picker:
            try:
                tool_names_out = await tool_picker.ainvoke(
                    input={"messages": state["messages"]}
                )
                tool_names = tool_names_out["parsed"].tool_names
                selected_tools = (
                    [tool for tool in tools if tool.name in tool_names]
                    if tool_names
                    else []
                )
            except Exception:
                logger.exception("Error picking tools, binding all")
                selected_tools = tools

        if selected_tools:
            bound = bound | chat_model.bind_tools(selected_tools)
        else:
            bound = bound | chat_model

        messages = await bound.ainvoke(
            {
                "messages": state["messages"],
            }
        )
        return {"messages": [messages]}

    builder = StateGraph(MessagesState)
    builder.add_node(chatbot)

    if hazard_classifier is not None:
        builder.add_node(input_guard)
        builder.add_edge(START, "input_guard")
        builder.add_edge("input_guard", "chatbot")
    else:
        builder.add_edge(START, "chatbot")

    if tool_node:
        builder.add_node(tool_node)
        builder.add_conditional_edges("chatbot", tools_condition)
        builder.add_edge("tools", "chatbot")
    else:
        builder.add_edge("chatbot", END)

    return builder.compile(checkpointer=checkpointer)


def _get_responding_at(inputs: dict[str, Any]) -> str:
    last_message: BaseMessage = inputs["messages"][-1]
    last_message_at = last_message.additional_kwargs.get("sent_at")
    responding_at = (
        datetime.fromisoformat(last_message_at)
        if last_message_at
        else datetime.now(tz=UTC)
    )
    return responding_at.strftime("%Y-%m-%d (%A)")
