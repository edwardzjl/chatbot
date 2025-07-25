from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

from langchain_core.messages import BaseMessage

from chatbot.utils import is_valid_positive_int

if TYPE_CHECKING:
    from langchain_core.language_models import BaseLanguageModel


logger = logging.getLogger(__name__)

DEFAULT_MESSAGE_CONTEXT_LENGTH = 20
DEFAULT_TOKEN_CONTEXT_LENGTH = 4096
DEFAULT_INPUT_TOKEN_RATIO = 0.8
MIN_POSITIVE_TOKENS = 1024


def resolve_token_management_params(
    chat_model: BaseLanguageModel,
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
    language_model: BaseLanguageModel,
    token_counter: (
        Callable[[list[BaseMessage]], int] | Callable[[BaseMessage], int] | None
    ) = None,
) -> tuple[Callable[[list[BaseMessage]], int] | Callable[[BaseMessage], int], bool]:
    effective_token_counter = token_counter
    if effective_token_counter is None:
        effective_token_counter = language_model.get_num_tokens_from_messages
        logger.info(
            "Using `get_num_tokens_from_messages` from language_model as token_counter."
        )

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
                "Calculated max_input_tokens: %d (capacity: %d - output_reservation: %d).",
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
            "Calculated max_input_tokens (%d) is not positive. Setting to a minimum of %d tokens.",
            max_input_tokens,
            MIN_POSITIVE_TOKENS,
        )
        max_input_tokens = MIN_POSITIVE_TOKENS

    return max_input_tokens


def _resolve_token_context_length(
    chat_model: BaseLanguageModel, user_context_length: int | None = None
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


def _get_model_max_output_tokens(chat_model: BaseLanguageModel) -> int | None:
    """Attempts to retrieve the model's maximum output tokens."""
    try:
        # Here I use ChatOpenAI's `max_tokens` attribute.
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
