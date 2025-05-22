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
from chatbot.utils import is_valid_positive_int

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.graph.graph import CompiledGraph


logger = logging.getLogger(__name__)


DEFAULT_MESSAGE_CONTEXT_LENGTH = 20
DEFAULT_TOKEN_CONTEXT_LENGTH = 4096
DEFAULT_INPUT_TOKEN_RATIO = 0.8
MIN_POSITIVE_TOKENS = 1024


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
    token_counter, max_input_tokens, _ = _resolve_token_management_params(
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


def _resolve_token_management_params(
    chat_model: BaseChatModel,
    token_counter: (
        Callable[[list[BaseMessage]], int] | Callable[[BaseMessage], int] | None
    ) = None,
    context_length: int | None = None,
) -> tuple[
    Callable[[list[BaseMessage]], int] | Callable[[BaseMessage], int], int, bool
]:
    """Determines the effective token counter, max input tokens, and if counting by messages.

    Returns:
        A tuple containing:
        - effective_token_counter: The function to use for counting.
        - max_input_tokens: The calculated maximum number of tokens/messages for input.
        - is_message_counting: Boolean indicating if counting is by messages (True) or tokens (False).
    """
    effective_token_counter, is_message_counting = _get_effective_token_counter(
        chat_model, token_counter
    )

    if is_message_counting:
        # When counting messages, max_input_tokens is the number of messages.
        # Default to 20 messages if no specific context_length for messages is given.
        max_input_tokens = (
            context_length
            if is_valid_positive_int(context_length)
            else DEFAULT_MESSAGE_CONTEXT_LENGTH
        )
        logger.info(
            "Truncating by message count: max_input_tokens set to %d messages.",
            max_input_tokens,
        )
        return effective_token_counter, max_input_tokens, is_message_counting

    # Token-based counting path
    resolved_context_length = _resolve_token_context_length(chat_model, context_length)
    model_max_output_tokens = _get_model_max_output_tokens(chat_model)

    max_input_tokens = _calculate_max_input_tokens(
        resolved_context_length, model_max_output_tokens
    )

    return effective_token_counter, max_input_tokens, is_message_counting


def _get_effective_token_counter(
    chat_model: BaseChatModel,
    token_counter: (
        Callable[[list[BaseMessage]], int] | Callable[[BaseMessage], int] | None
    ) = None,
) -> tuple[Callable[[list[BaseMessage]], int] | Callable[[BaseMessage], int], bool]:
    effective_token_counter = token_counter
    if effective_token_counter is None:
        try:
            effective_token_counter = chat_model.get_num_tokens_from_messages
            logger.info(
                "Using `get_num_tokens_from_messages` from chat_model as token_counter."
            )
        except AttributeError:
            logger.warning(
                "Chat model lacks `get_num_tokens_from_messages`. "
                "Falling back to message count (len) for truncation. "
                "This may lead to context overflow if model expects token limits."
            )
            effective_token_counter = len

    is_message_counting = effective_token_counter is len
    return effective_token_counter, is_message_counting


def _calculate_max_input_tokens(
    resolved_context_length: int, model_max_output_tokens: int | None = None
) -> int:
    """Calculates the maximum input tokens based on context length and output reservation."""
    if model_max_output_tokens is not None:
        if resolved_context_length > model_max_output_tokens:
            max_input_tokens = resolved_context_length - model_max_output_tokens
            logger.info(
                "Calculated max_input_tokens: %d "
                "(capacity: %d - output_reservation: %d).",
                max_input_tokens,
                resolved_context_length,
                model_max_output_tokens,
            )
        else:
            logger.warning(
                "Model's max_output_tokens (%d) is >= resolved_context_length (%d). "
                "Using %.0f%% of capacity for input.",
                model_max_output_tokens,
                resolved_context_length,
                DEFAULT_INPUT_TOKEN_RATIO * 100,
            )
            max_input_tokens = int(resolved_context_length * DEFAULT_INPUT_TOKEN_RATIO)
    else:
        logger.info(
            "Model's max_output_tokens not available/invalid. Using %.0f%% of resolved_context_length for input.",
            DEFAULT_INPUT_TOKEN_RATIO * 100,
        )
        max_input_tokens = int(resolved_context_length * DEFAULT_INPUT_TOKEN_RATIO)

    if max_input_tokens <= 0:
        logger.warning(
            "Calculated max_input_tokens (%d) is not positive. "
            "Setting to a minimum of %d tokens.",
            max_input_tokens,
            MIN_POSITIVE_TOKENS,
        )
        max_input_tokens = MIN_POSITIVE_TOKENS

    return max_input_tokens


def _resolve_token_context_length(
    chat_model: BaseChatModel, user_context_length: int | None = None
) -> int:
    """Resolves the context length when counting by tokens."""
    if is_valid_positive_int(user_context_length):
        logger.info(
            "Using user-provided context_length: %d tokens.", user_context_length
        )
        return user_context_length

    if user_context_length is not None:
        logger.warning(
            "Invalid user-provided context_length (%s). Trying to get from model.",
            user_context_length,
        )

    try:
        # `get_context_length` is my custom method for ChatOpenAI.
        model_ctx_len = chat_model.get_context_length()
        if is_valid_positive_int(model_ctx_len):
            logger.info(
                "Using context_length from chat_model: %d tokens.", model_ctx_len
            )
            return model_ctx_len
        elif model_ctx_len is not None:
            logger.warning(
                "Chat model's get_context_length() returned invalid value: %s.",
                model_ctx_len,
            )
    except AttributeError:
        logger.warning(
            "Chat model lacks get_context_length. User did not provide valid context_length. "
        )
    except Exception as e:  # Catching general exceptions during attribute access
        logger.exception(
            "Unexpected error accessing chat_model.get_context_length: %s.", e
        )

    logger.warning(
        "Using default context_length: %d tokens (model/user value unavailable/invalid).",
        DEFAULT_TOKEN_CONTEXT_LENGTH,
    )
    return DEFAULT_TOKEN_CONTEXT_LENGTH


def _get_model_max_output_tokens(chat_model: BaseChatModel) -> int | None:
    """Attempts to retrieve the model's maximum output tokens."""
    try:
        raw_model_max_tokens = getattr(chat_model, "max_tokens", None)
        if is_valid_positive_int(raw_model_max_tokens):
            return raw_model_max_tokens
        elif raw_model_max_tokens is not None:
            logger.warning(
                "Chat model's max_tokens attribute (%s) is invalid. Not using for calculation.",
                raw_model_max_tokens,
            )
    except Exception as e:
        # Using a more specific exception if known (e.g., TypeError, ValueError)
        logger.exception(
            "Unexpected error accessing chat_model.max_tokens: %s. Not using for calculation.",
            e,
        )
    return None


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
