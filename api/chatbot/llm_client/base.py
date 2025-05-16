import logging
import re
from typing import Any, AsyncIterator, Iterator, Literal, TypedDict, override

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.load.serializable import Serializable
from langchain_core.messages import AIMessage, BaseMessage, convert_to_openai_messages
from langchain_core.outputs import ChatGenerationChunk
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import _construct_responses_api_payload
from pydantic import PrivateAttr, Field


logger = logging.getLogger(__name__)


class MessageChunk(TypedDict):
    data: str
    type: Literal["text", "thought"]
    index: int


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
    _buffering_signature: str | None = PrivateAttr(default=None)
    """The current buffering signature. None means not buffering."""
    _buffer: str = PrivateAttr(default="")
    _index: int = PrivateAttr(default=0)
    """The index of each chunk. Chunks with the same index should be merged together.
    See <https://github.com/langchain-ai/langchain/blob/d4f77a8c8fae9a6a33e55d572ee9e034c762eeb0/libs/core/langchain_core/utils/_merge.py#L92C1-L93C1>
    This is not strictly increasing one by one.
    """

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
        self._buffer = ""
        self._buffering_signature = None
        self._index = 0

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
        if self.thinking:
            return self._process_token(
                token, "thought", self.stop_thinking_signature, "text"
            )
        else:
            return self._process_token(
                token, "text", self.thinking_signature, "thought"
            )

    def _process_token(
        self,
        token: str,
        chunk_type: Literal["text", "thought"],
        signature: str,
        chunk_type_after_match: Literal["text", "thought"],
    ) -> MessageChunk | None:
        """Handles token processing for entering or exiting a mode.

        Args:
            token (str): The token to process.
            chunk_type (Literal["text", "thought"]): The type of chunk when exiting the mode.
            signature (str): The signature to detect. For example, "<think>" or "</think>".
            chunk_type_after_match (Literal["text", "thought"]): The type of chunk after matching the signature.

        Returns:
            MessageChunk | None: A dictionary with "data" and "type" keys, or None if buffering.
        """
        if token == "":
            return MessageChunk(data="", type=chunk_type, index=self._index)
        if self._buffering_signature is None:
            # Not currently buffering
            if token == signature:
                self._toggle_mode(chunk_type_after_match == "thought")
                return None
            elif token.startswith(signature):
                # token is longer than the signature
                self._toggle_mode(chunk_type_after_match == "thought")
                return MessageChunk(
                    data=token.removeprefix(signature),
                    type=chunk_type_after_match,
                    index=self._index,
                )
            elif signature.startswith(token):
                # token is shorter than the signature
                self._start_buffering(token, signature)
                return None
            else:
                return MessageChunk(data=token, type=chunk_type, index=self._index)
        else:
            # Currently buffering
            self._buffer += token
            if self._buffer == signature:
                # Buffer matches the signature exactly
                self._toggle_mode(chunk_type_after_match == "thought")
                self._clear_buffer()
                return None
            elif self._buffer.startswith(signature):
                # Buffer is longer than the signature
                self._toggle_mode(chunk_type_after_match == "thought")
                remaining = self._buffer.removeprefix(signature)
                self._clear_buffer()
                return MessageChunk(
                    data=remaining,
                    type=chunk_type_after_match,
                    index=self._index,
                )
            elif signature.startswith(self._buffer):
                # Buffer is shorter than the signature, continue buffering
                return None
            else:
                chunk = MessageChunk(
                    data=self._buffer, type=chunk_type, index=self._index
                )
                self._clear_buffer()
                return chunk

    def _toggle_mode(self, entering_thinking: bool) -> None:
        """Toggles the thinking mode and increments the index on mode change."""
        if self.thinking != entering_thinking:
            self._index += 1  # Increment index on mode change
        self.thinking = entering_thinking

    def _start_buffering(self, token: str, signature: str) -> None:
        """Starts buffering for a signature."""
        self._buffer = token
        self._buffering_signature = signature

    def _clear_buffer(self) -> None:
        """Clears the buffer and resets buffering state."""
        self._buffer = ""
        self._buffering_signature = None


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
        # Below is a temporary solution before <https://github.com/langchain-ai/langchain/pull/31226>
        # gets merged.

        # section supersuper

        messages = self._convert_input(input_).to_messages()

        # section my patch 1

        # It seems that we are safe to manipulate the `lc_messages` here for the following reasons:
        # - `langchain_core.prompt_values.ChatPromptValue.to_messages` calls `list(self.messages)`, which will create a new list.
        for lc_message in messages:
            self.patch_content(lc_message)

        # endsection my patch 1

        if stop is not None:
            kwargs["stop"] = stop

        payload = {**self._default_params, **kwargs}
        if self._use_responses_api(payload):
            payload = _construct_responses_api_payload(messages, payload)
        else:
            # Use `convert_to_openai_messages` instead of `_convert_message_to_dict`
            payload["messages"] = convert_to_openai_messages(messages)

        # endsection supersuper

        # section super

        if "max_tokens" in payload:
            payload["max_completion_tokens"] = payload.pop("max_tokens")

        # Mutate system message role to "developer" for o-series models
        if self.model_name and re.match(r"^o\d", self.model_name):
            for message in payload.get("messages", []):
                if message["role"] == "system":
                    message["role"] = "developer"

        # endsection super

        payload["messages"] = self._truncate_multi_modal_contents(payload["messages"])

        return payload

    def _process(self, chunk: ChatGenerationChunk) -> ChatGenerationChunk:
        token = chunk.message.content
        if not isinstance(token, str):
            logger.warning("LLM generated non string content: %s", token)
            return chunk
        # record the raw output before we determine the type
        chunk.message.additional_kwargs["raw_content"] = token

        message_chunk = self.thinking_processor.on_token(token)
        if not message_chunk:
            # If a `ChatGenerationChunk` exists but no `message_chunk` is produced after processing the token,
            # it indicates the token might be part of the thinking prefix or suffix.
            # In other words, we are either "entering" or "exiting" the thinking mode.
            # It is essential to yield this chunk; otherwise, part of the `raw_content` will be lost.
            chunk.message.content = []
        elif message_chunk["type"] == "text":
            # Even it's a text, the content might be modified by the thinking processor.
            chunk.message.content = [
                {
                    "type": "text",
                    "text": message_chunk["data"],
                    "index": message_chunk["index"],
                }
            ]
        elif message_chunk["type"] == "thought":
            chunk.message.content = [
                {
                    "type": "thinking",
                    "thinking": message_chunk["data"],
                    "index": message_chunk["index"],
                }
            ]
        else:
            logger.warning("Unknown message type: %s", message_chunk["type"])
        return chunk

    def _truncate_multi_modal_contents(self, messages: list[dict]) -> list[dict]:
        """Limit the number of multimodal content in the messages.

        Args:
            messages (list[dict]): OpenAI messages.
        """
        if not messages:  # Will this happen?
            return messages

        if (
            limit_mm_per_prompt := (self.metadata or {}).get("limit_mm_per_prompt")
        ) is None:
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

    def patch_content(self, lc_message: BaseMessage) -> None:
        if (
            isinstance(lc_message, AIMessage)
            and (raw_content := lc_message.additional_kwargs.get("raw_content"))
            is not None
        ):
            lc_message.content = raw_content

        if attachments := lc_message.additional_kwargs.get("attachments"):
            lc_message.content = attach_attachments(lc_message.content, attachments)


def attach_attachments(content: str | list[dict[str, Any]], attachments: list) -> list:
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

    def process_attachment(attachment: dict[str, Any]) -> dict[str, Any] | None:
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
