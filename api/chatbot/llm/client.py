import logging
from typing import Any, AsyncIterator, Iterator, Literal, TypedDict, override

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.load.serializable import Serializable
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGenerationChunk
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import _convert_message_to_dict
from pydantic import PrivateAttr, Field


logger = logging.getLogger(__name__)


class MessageChunk(TypedDict):
    data: str
    type: Literal["text", "thought"]


class StreamThinkingProcessor(Serializable):
    """Processes a stream of tokens to identify and separate "thinking" sections
    from regular text based on start and stop thinking signatures.

    The class maintains a state to track whether it is currently in a "thinking" state
    and uses buffers to handle partial signature matches in the token stream.
    """

    default_thinking: bool = False
    """If True, the processor starts in "thinking" mode.
    If False, it starts in "text" mode, processing text until the `thinking_signature` is encountered.
    """
    thinking_signature: str = "<think>"
    """The string signature that indicates the start of a "thinking" section."""
    stop_thinking_signature: str = "</think>"
    """The string signature that indicates the end of a "thinking" section."""

    # I cannot use `PrivateAttr` for `thinking` as `default_thinking` in `default_factory` is not a `PrivateAttr`
    thinking: bool = Field(default_factory=lambda data: data["default_thinking"])
    _maybe_start_thinking: bool = PrivateAttr(default=False)
    _maybe_stop_thinking: bool = PrivateAttr(default=False)
    _buffer: str = PrivateAttr(default="")

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this model can be serialized by Langchain."""
        return True

    @classmethod
    def get_lc_namespace(cls) -> list[str]:
        """Return the namespace of this model."""
        return ["chatbot", "llm", "client"]

    def reset(self) -> None:
        """Resets the processor to its initial state, as defined by default_thinking.
        Clears internal buffers and sets the thinking state to default.
        """
        self.thinking = self.default_thinking
        self._maybe_start_thinking = False
        self._maybe_stop_thinking = False
        self._buffer = ""

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
                not self._maybe_start_thinking
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
                    self._maybe_start_thinking = True
                    self._buffer = token
                else:
                    # Regular text token, not related to thinking signatures. Return as "text" chunk.
                    return {"data": token, "type": "text"}
            else:  # `self.maybe_start_thinking is True`:  Currently buffering to detect thinking start signature.
                self._buffer += token  # Append current token to the buffer.
                if self._buffer.startswith(
                    self.thinking_signature
                ):  # buffer may be longer than thinking_signature
                    # Buffer now starts with the thinking signature. Enter "thinking" mode.
                    self.thinking = True
                    self._maybe_start_thinking = (
                        False  # Stop looking for start signature.
                    )
                    remaining = self._buffer.removeprefix(self.thinking_signature)
                    if remaining:
                        # If buffer contains data after the signature, return it as "thought" chunk.
                        return {"data": remaining, "type": "thought"}
                elif self.thinking_signature.startswith(self._buffer):
                    # Buffer is still a prefix of the thinking signature. Continue buffering.
                    return None  # No chunk to return yet, still buffering.
                else:
                    # Buffer is no longer related to thinking signature. It was just regular text.
                    self._maybe_start_thinking = (
                        False  # Stop looking for start signature.
                    )
                    data = self._buffer  # Return the buffered data as "text" chunk.
                    self._buffer = ""  # Clear buffer.
                    return {"data": data, "type": "text"}
        else:  # `self.thinking is True`: Currently in "thinking" mode.
            if (
                not self._maybe_stop_thinking
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
                    self._maybe_stop_thinking = True
                    self._buffer = token
                else:
                    # Regular thought token, not related to stop thinking signature. Return as "thought" chunk.
                    return {"data": token, "type": "thought"}
            else:  # self.maybe_stop_thinking is True: Currently buffering to detect thinking stop signature.
                self._buffer += token  # Append current token to buffer.
                if self._buffer.startswith(
                    self.stop_thinking_signature
                ):  # buffer may be longer than stop_thinking_signature
                    # Buffer now starts with stop thinking signature. Exit "thinking" mode.
                    remaining = self._buffer.removeprefix(self.stop_thinking_signature)
                    self.reset()  # Reset state for next thinking section detection.
                    self.thinking = False  # NOTE!: ENSURE we exit thinking mode, regardless of default_thinking
                    if remaining:
                        # If buffer contains data after the signature, return it as "text" chunk.
                        return {"data": remaining, "type": "text"}
                elif self.stop_thinking_signature.startswith(self._buffer):
                    # Buffer is still a prefix of the stop thinking signature. Continue buffering.
                    return None  # No chunk to return yet, still buffering.
                else:
                    # Buffer is no longer related to stop thinking signature. It was just a thought.
                    self._maybe_stop_thinking = (
                        False  # Stop looking for stop signature.
                    )
                    data = self._buffer  # Return the buffered data as "thought" chunk.
                    self._buffer = ""  # Clear buffer.
                    return {"data": data, "type": "thought"}


class ReasoningChatOpenai(ChatOpenAI):
    thinking_processor: StreamThinkingProcessor = StreamThinkingProcessor()

    @override
    @classmethod
    def get_lc_namespace(cls) -> list[str]:
        """Get the namespace of the langchain object."""
        return ["chatbot", "llm", "client"]

    @override
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

    @override
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

    @override
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

        dict_messages = [_convert_message_to_dict_patch(m) for m in messages]

        if (
            limit_mm_per_prompt := (self.metadata or {}).get("limit_mm_per_prompt")
        ) is not None:
            dict_messages = _limit_mm_input(dict_messages, limit_mm_per_prompt)

        return {
            "messages": dict_messages,
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


def convert_attachments(content, attachments: list) -> list:
    """Convert and append the attachments into content to be compatible with OpenAI's Chat API."""

    if isinstance(content, str):
        content = [{"type": "text", "text": content}]

    if not isinstance(content, list):
        logger.warning(
            "The content is not a string or list. Skipping the attachments conversion."
        )
        return content

    mimetype_map = {
        "image/": "image_url",
        "video/": "video_url",
    }

    def process_attachment(attachment: dict[str, Any]) -> dict[str, str] | None:
        mimetype: str = attachment.get("mimetype")
        if not mimetype:
            logger.warning(
                "Attachment %s does not have a mimetype. Skipping.", attachment
            )
            return None

        url = attachment.get("url")
        if not url:
            logger.warning("Attachment %s does not have a URL. Skipping.", attachment)
            return None

        for prefix, content_type in mimetype_map.items():
            if mimetype.startswith(prefix):
                return {"type": content_type, content_type: {"url": url}}

        logger.warning(
            "Skipping unsupported attachment. Mimetype: %s, URL: %s", mimetype, url
        )
        return None

    processed_attachments = filter(
        None, (process_attachment(attachment) for attachment in attachments)
    )
    content.extend(processed_attachments)

    return content


def _convert_message_to_dict_patch(message: BaseMessage) -> dict:
    """Converts a BaseMessage to a dictionary, with additional handling for AIMessage raw_output.
    This is a hack to work around the 'thought' part extracted by `StreamThinkingProcessor`,
    and attribute dis-alignment when submitting multimodal messages.

    OpenAI's Chat API expects the content to be a list of dictionaries, where each dictionary
    represents a modality. While in my app, the content is always a string, and I put other things like
    attachments in the `additional_kwargs` attribute.

    This has to be done here, during converting the `BaseMessage` object to dict, before sending to the LLM.
    Or langchain could somehow persist the patched message and destroy my app.
    """
    res = _convert_message_to_dict(message)
    if (
        isinstance(message, AIMessage)
        and (raw_output := message.additional_kwargs.get("raw_output")) is not None
    ):
        res["content"] = raw_output

    if attachments := message.additional_kwargs.get("attachments"):
        res["content"] = convert_attachments(res["content"], attachments)
    return res


def _limit_mm_input(messages: list[dict], limit_mm_per_prompt) -> list[dict]:
    if not messages:  # fast return
        return messages

    def parse_limit(key: str) -> int:
        value = limit_mm_per_prompt.get(key, 1)
        try:
            return int(value)
        except (ValueError, TypeError):
            logging.error(
                "Invalid value for '%s' in limit_mm_per_prompt: %s, using default 1",
                key,
                value,
            )
            return 1

    limit_image_per_prompt = parse_limit("image")
    limit_video_per_prompt = parse_limit("video")

    current_images = 0
    current_videos = 0

    # The goal is to keep the latest multimodal content in the messages.
    # So I reversly iterate the messages and filter out the multimodal content
    for message in reversed(messages):
        content = message["content"]
        if not isinstance(content, list):
            continue

        # Same here, I want to keep the latest multimodal content in the message.
        for i in range(len(content) - 1, -1, -1):
            part = content[i]
            if not isinstance(part, dict):
                continue

            part_type = part.get("type")
            if part_type == "image_url":
                if current_images < limit_image_per_prompt:
                    current_images += 1
                else:
                    del content[i]
            elif part_type == "video_url":
                if current_videos < limit_video_per_prompt:
                    current_videos += 1
                else:
                    del content[i]

    return messages
