from typing import Callable

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, trim_messages
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from chatbot.llm_client.vllm import VLLMChatOpenAI

from .token_management import resolve_token_management_params

tmpl = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are Rei, the ideal assistant dedicated to assisting users effectively.",
        ),
        ("placeholder", "{messages}"),
        (
            "system",
            """Provide a concise summary of the entire conversation above.
- Focus on the overall topic or outcome, not individual messages.
- Keep it under 10 words.
- Use the same language as the user.""",
        ),
    ]
)
output_parser = StrOutputParser()


def create_summary_agent(
    chat_model: BaseChatModel,
    *,
    token_counter: Callable[[list[BaseMessage]], int]
    | Callable[[BaseMessage], int]
    | None = None,
    context_length: int | None = None,
) -> Runnable:
    token_counter, max_input_tokens, _ = resolve_token_management_params(
        chat_model, token_counter, context_length
    )

    # Notice we don't pass in messages. This creates
    # a RunnableLambda that takes messages as input
    trimmer = trim_messages(
        token_counter=token_counter,
        max_tokens=max_input_tokens,
        start_on="human",
        include_system=True,
    )

    # Disable internal "thinking" behavior when using reasoning models.
    # NOTE: This only applies when using the VLLM-based chat service.
    if isinstance(chat_model, VLLMChatOpenAI):
        extra_body = chat_model.extra_body or {}
        extra_body = extra_body | {"chat_template_kwargs": {"enable_thinking": False}}
        chat_model = chat_model.bind(extra_body=extra_body)

    return tmpl | trimmer | chat_model | output_parser
