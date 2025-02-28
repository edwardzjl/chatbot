from datetime import datetime, timezone
from typing import Any, AsyncIterator, Iterator, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGenerationChunk
from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_openai import ChatOpenAI


def utcnow():
    """
    `datetime.datetime.utcnow()` does not contain timezone information.
    """
    return datetime.now(timezone.utc)


class MessageChunk(TypedDict):
    data: str
    type: Literal["text", "thought"]


class StreamThinkingProcessor:
    def __init__(
        self,
        thinking_signature: str = "<think>",
        stop_thinking_signature: str = "</think>",
    ) -> None:
        self.thinking_signature = thinking_signature
        self.stop_thinking_signature = stop_thinking_signature
        self.reset()

    def reset(self) -> None:
        self.thinking = False
        self.maybe_start_thinking = False
        self.maybe_stop_thinking = False
        self.buffer = ""

    def on_token(self, token: str) -> MessageChunk | None:
        if not self.thinking:
            if not self.maybe_start_thinking:
                if token.startswith(self.thinking_signature):
                    self.thinking = True
                    remaining = token.removeprefix(self.thinking_signature)
                    if remaining:
                        return {"data": remaining, "type": "thought"}
                elif self.thinking_signature.startswith(token):
                    self.maybe_start_thinking = True
                    self.buffer = token
                else:
                    # Not a crucial token at all, just return it.
                    return {"data": token, "type": "text"}
            else:  # maybe_start_thinking
                self.buffer += token
                # buffer may be longer than thinking_signature
                if self.buffer.startswith(self.thinking_signature):
                    self.thinking = True
                    self.maybe_start_thinking = False
                    remaining = self.buffer.removeprefix(self.thinking_signature)
                    if remaining:
                        return {"data": remaining, "type": "thought"}
                elif self.thinking_signature.startswith(self.buffer):
                    # Not reached `self.thinking_signature` yet.
                    return
                else:
                    # maybe_start_thinking but buffer is not a thinking_signature
                    # return buffer and reset
                    self.maybe_start_thinking = False
                    data = self.buffer
                    self.buffer = ""
                    return {"data": data, "type": "text"}
        else:  # thinking
            if not self.maybe_stop_thinking:
                if token.startswith(self.stop_thinking_signature):
                    self.reset()
                    remaining = token.removeprefix(self.stop_thinking_signature)
                    if remaining:
                        return {"data": remaining, "type": "text"}
                elif self.stop_thinking_signature.startswith(token):
                    self.maybe_stop_thinking = True
                    self.buffer = token
                else:
                    # Not a crucial token at all, just return it.
                    return {"data": token, "type": "thought"}
            else:  # maybe_stop_thinking
                self.buffer += token
                # buffer may be longer than stop_thinking_signature
                if self.buffer.startswith(self.stop_thinking_signature):
                    remaining = self.buffer.removeprefix(self.stop_thinking_signature)
                    self.reset()
                    if remaining:
                        return {"data": remaining, "type": "text"}
                elif self.stop_thinking_signature.startswith(self.buffer):
                    # Not reached `self.stop_thinking_signature` yet.
                    return
                else:
                    # maybe_stop_thinking but buffer is not a stop_thinking_signature
                    # return buffer and reset
                    self.maybe_stop_thinking = False
                    data = self.buffer
                    self.buffer = ""
                    return {"data": data, "type": "thought"}


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

    def _process(self, chunk: ChatGenerationChunk) -> ChatGenerationChunk:
        token = chunk.message.content
        if not isinstance(token, str):
            return chunk
        message_chunk = self.thinking_processor.on_token(token)
        if not message_chunk:
            # If there's `ChatGenerationChunk` but no message_chunk after processing token,
            # it means the token might be part of the thinking prefix / suffix.
            chunk.message.content = ""
            chunk.message.additional_kwargs["raw_output"] = token
            return chunk
        if message_chunk["type"] == "text":
            return chunk
        else:
            chunk.message.content = ""
            chunk.message.additional_kwargs["raw_output"] = token
            chunk.message.additional_kwargs["text_type"] = "thought"
            chunk.message.additional_kwargs["thought"] = message_chunk["data"]
            return chunk
