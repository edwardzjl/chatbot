from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Callable

from langchain_core.messages import BaseMessage, SystemMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, MessagesState, StateGraph

from chatbot.safety import create_hazard_classifier, hazard_categories

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.graph.graph import CompiledGraph


def create_agent(
    chat_model: BaseChatModel,
    *,
    safety_model: BaseChatModel | None = None,
    checkpointer: BaseCheckpointSaver = None,
    token_counter: (
        Callable[[list[BaseMessage]], int] | Callable[[BaseMessage], int] | None
    ) = None,
    max_tokens: int = 20,
) -> CompiledGraph:
    if token_counter is None:
        if hasattr(chat_model, "get_num_tokens_from_messages"):
            token_counter = chat_model.get_num_tokens_from_messages
        else:
            token_counter = len

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
                # patch the hazard category to the last message
                last_message.additional_kwargs = last_message.additional_kwargs | {
                    "hazard": category
                }
                return {"messages": [last_message]}
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

    async def chatbot(state: MessagesState) -> MessagesState:
        """Process the current state and generate a response using the LLM."""

        instruction = """You are Rei, the ideal assistant dedicated to assisting users effectively. Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity.
When solving problems, decompose them into smaller parts and solve parts one by one sequentially.
State the initial condition clearly and make one change at a time, verifying the result after each modification.

Current date: {date}
"""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", instruction),
                ("placeholder", "{messages}"),
            ]
        )

        bound = prompt | chat_model

        hint_message = None
        if hazard := state["messages"][-1].additional_kwargs.get("hazard"):
            hint_message = SystemMessage(
                content=f"""The user input may contain inproper content related to:
{hazard_categories.get(hazard)}

Please respond with care and professionalism. Avoid engaging with harmful or unethical content. Instead, guide the user towards more constructive and respectful communication."""
            )

        all_messages = (
            state["messages"] + hint_message if hint_message else state["messages"]
        )
        windowed_messages: list[BaseMessage] = trim_messages(
            all_messages,
            token_counter=token_counter,
            max_tokens=max_tokens,
            start_on="human",  # This means that the first message should be from the user after trimming.
        )

        messages = await bound.ainvoke(
            {
                "messages": windowed_messages,
                "date": datetime.datetime.now(
                    tz=datetime.UTC
                ).date(),  # TODO: get the current date from the user?
            }
        )
        return {"messages": [messages]}

    builder = StateGraph(MessagesState)
    builder.add_node(input_guard)
    builder.add_node(chatbot)

    builder.add_edge(START, "input_guard")
    builder.add_edge("input_guard", "chatbot")
    builder.add_edge("chatbot", END)

    return builder.compile(checkpointer=checkpointer)
