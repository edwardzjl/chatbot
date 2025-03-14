from datetime import datetime, timezone
from typing import Any, AsyncIterator, Iterator, Literal, TypedDict

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGenerationChunk
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import _convert_message_to_dict


def utcnow():
    """
    `datetime.datetime.utcnow()` does not contain timezone information.
    """
    return datetime.now(timezone.utc)


class MessageChunk(TypedDict):
    data: str
    type: Literal["text", "thought"]


class StreamThinkingProcessor:
    """Processes a stream of tokens to identify and separate "thinking" sections
    from regular text based on start and stop thinking signatures.

    The class maintains a state to track whether it is currently in a "thinking" state
    and uses buffers to handle partial signature matches in the token stream.
    """

    def __init__(
        self,
        default_thinking: bool = False,
        thinking_signature: str = "<think>",
        stop_thinking_signature: str = "</think>",
    ) -> None:
        """Initializes the StreamThinkingProcessor.

        Args:
            default_thinking (bool): If True, the processor starts in "thinking" mode.
                                     If False, it starts in "text" mode, processing text until
                                     the thinking_signature is encountered.
            thinking_signature (str): The string signature that indicates the start of a "thinking" section.
            stop_thinking_signature (str): The string signature that indicates the end of a "thinking" section.
        """
        self.thinking_signature = thinking_signature
        self.stop_thinking_signature = stop_thinking_signature
        self.default_thinking = default_thinking
        self.reset()

    def reset(self) -> None:
        """Resets the processor to its initial state, as defined by default_thinking.
        Clears internal buffers and sets the thinking state to default.
        """
        self.thinking = self.default_thinking
        self.maybe_start_thinking = False
        self.maybe_stop_thinking = False
        self.buffer = ""

    def on_token(self, token: str) -> MessageChunk | None:
        """Processes a single token from the stream.

        This method checks the token against the thinking and stop thinking signatures
        to determine if the processor should enter or exit "thinking" mode.
        It returns a MessageChunk dictionary indicating the type of content ("text" or "thought")
        and the data to be processed further.

        Args:
            token (str): The token to process.

        Returns:
            MessageChunk | None: A dictionary with "data" and "type" keys, or None if no chunk is ready to be returned
                                    (e.g., when buffering for signature detection).
        """
        if not self.thinking:  # Currently in "text" mode.
            if (
                not self.maybe_start_thinking
            ):  # Not currently looking for thinking start signature.
                if token.startswith(self.thinking_signature):
                    # Token starts with the thinking signature. Enter "thinking" mode.
                    self.thinking = True
                    remaining = token.removeprefix(self.thinking_signature)
                    if remaining:
                        # If the token contains data after the signature, return it as a "thought" chunk.
                        return {"data": remaining, "type": "thought"}
                elif self.thinking_signature.startswith(token):
                    # Token is a prefix of the thinking signature. Start buffering.
                    self.maybe_start_thinking = True
                    self.buffer = token
                else:
                    # Regular text token, not related to thinking signatures. Return as "text" chunk.
                    return {"data": token, "type": "text"}
            else:  # `self.maybe_start_thinking is True`:  Currently buffering to detect thinking start signature.
                self.buffer += token  # Append current token to the buffer.
                if self.buffer.startswith(
                    self.thinking_signature
                ):  # buffer may be longer than thinking_signature
                    # Buffer now starts with the thinking signature. Enter "thinking" mode.
                    self.thinking = True
                    self.maybe_start_thinking = (
                        False  # Stop looking for start signature.
                    )
                    remaining = self.buffer.removeprefix(self.thinking_signature)
                    if remaining:
                        # If buffer contains data after the signature, return it as "thought" chunk.
                        return {"data": remaining, "type": "thought"}
                elif self.thinking_signature.startswith(self.buffer):
                    # Buffer is still a prefix of the thinking signature. Continue buffering.
                    return None  # No chunk to return yet, still buffering.
                else:
                    # Buffer is no longer related to thinking signature. It was just regular text.
                    self.maybe_start_thinking = (
                        False  # Stop looking for start signature.
                    )
                    data = self.buffer  # Return the buffered data as "text" chunk.
                    self.buffer = ""  # Clear buffer.
                    return {"data": data, "type": "text"}
        else:  # `self.thinking is True`: Currently in "thinking" mode.
            if (
                not self.maybe_stop_thinking
            ):  # Not currently looking for thinking stop signature.
                if token.startswith(self.stop_thinking_signature):
                    # Token starts with the stop thinking signature. Exit "thinking" mode.
                    self.reset()  # Reset state for next thinking section detection.
                    self.thinking = False  # NOTE!: ENSURE we exit thinking mode, regardless of default_thinking
                    remaining = token.removeprefix(self.stop_thinking_signature)
                    if remaining:
                        # If the token contains data after the signature, return it as a "text" chunk.
                        return {"data": remaining, "type": "text"}
                elif self.stop_thinking_signature.startswith(token):
                    # Token is a prefix of the stop thinking signature. Start buffering.
                    self.maybe_stop_thinking = True
                    self.buffer = token
                else:
                    # Regular thought token, not related to stop thinking signature. Return as "thought" chunk.
                    return {"data": token, "type": "thought"}
            else:  # self.maybe_stop_thinking is True: Currently buffering to detect thinking stop signature.
                self.buffer += token  # Append current token to buffer.
                if self.buffer.startswith(
                    self.stop_thinking_signature
                ):  # buffer may be longer than stop_thinking_signature
                    # Buffer now starts with stop thinking signature. Exit "thinking" mode.
                    remaining = self.buffer.removeprefix(self.stop_thinking_signature)
                    self.reset()  # Reset state for next thinking section detection.
                    self.thinking = False  # NOTE!: ENSURE we exit thinking mode, regardless of default_thinking
                    if remaining:
                        # If buffer contains data after the signature, return it as "text" chunk.
                        return {"data": remaining, "type": "text"}
                elif self.stop_thinking_signature.startswith(self.buffer):
                    # Buffer is still a prefix of the stop thinking signature. Continue buffering.
                    return None  # No chunk to return yet, still buffering.
                else:
                    # Buffer is no longer related to stop thinking signature. It was just a thought.
                    self.maybe_stop_thinking = False  # Stop looking for stop signature.
                    data = self.buffer  # Return the buffered data as "thought" chunk.
                    self.buffer = ""  # Clear buffer.
                    return {"data": data, "type": "thought"}


def _convert_message_to_dict_patch(message: BaseMessage) -> dict:
    """Converts a BaseMessage to a dictionary, with additional handling for AIMessage raw_output.
    This is a hack to work around the 'thought' part extracted by `StreamThinkingProcessor`.
    """
    res = _convert_message_to_dict(message)
    if (
        isinstance(message, AIMessage)
        and (raw_output := message.additional_kwargs.get("raw_output")) is not None
    ):
        res["content"] = raw_output
    return res


class ReasoningChatOpenai(ChatOpenAI):
    thinking_processor: StreamThinkingProcessor = StreamThinkingProcessor()

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        self.thinking_processor.reset()
        for chunk in super()._stream(
            messages, stop=stop, run_manager=run_manager, **kwargs
        ):
            yield self._process(chunk)

    async def _astream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: AsyncCallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        self.thinking_processor.reset()
        async for chunk in super()._astream(
            messages, stop=stop, run_manager=run_manager, **kwargs
        ):
            yield self._process(chunk)

    def _get_request_payload(
        self,
        input_: LanguageModelInput,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> dict:
        messages = self._convert_input(input_).to_messages()
        if stop is not None:
            kwargs["stop"] = stop

        return {
            "messages": [_convert_message_to_dict_patch(m) for m in messages],
            **self._default_params,
            **kwargs,
        }

    def _process(self, chunk: ChatGenerationChunk) -> ChatGenerationChunk:
        token = chunk.message.content
        if not isinstance(token, str):
            return chunk
        message_chunk = self.thinking_processor.on_token(token)
        chunk.message.additional_kwargs["raw_output"] = (
            token  # record the raw output before we determine the type
        )
        if not message_chunk:
            # If there's `ChatGenerationChunk` but no message_chunk after processing token,
            # it means the token might be part of the thinking prefix / suffix.
            chunk.message.content = ""
            return chunk
        if message_chunk["type"] == "text":
            # Even it's a text, the content might be modified by the thinking processor.
            chunk.message.content = message_chunk["data"]
            return chunk
        else:
            chunk.message.content = ""
            chunk.message.additional_kwargs["thought"] = message_chunk["data"]
            return chunk
