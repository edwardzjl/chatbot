from typing import Any, Optional
from uuid import UUID

from fastapi import WebSocket
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult

from chatbot.schemas import ChatMessage


class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self, websocket: WebSocket, conversation_id: str):
        self.websocket = websocket
        self.conversation_id = conversation_id

    async def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        message = ChatMessage(
            id=run_id,
            conversation=self.conversation_id,
            from_="ai",
            content=None,
            type="stream/start",
        )
        await self.websocket.send_text(message.model_dump_json())

    async def on_llm_new_token(
        self,
        token: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        message = ChatMessage(
            id=run_id,
            conversation=self.conversation_id,
            from_="ai",
            content=token,
            type="stream/text",
        )
        await self.websocket.send_text(message.model_dump_json())

    async def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        message = ChatMessage(
            id=run_id,
            conversation=self.conversation_id,
            from_="ai",
            content=None,
            type="stream/end",
        )
        await self.websocket.send_text(message.model_dump_json())
        # send the full message again in case user switched to another tab
        # so that the frontend can update the message
        full_message = ChatMessage(
            id=run_id,
            conversation=self.conversation_id,
            from_="ai",
            content=response.generations[0][0].text,
            type="text",
        )
        await self.websocket.send_text(full_message.model_dump_json())

    async def on_llm_error(
        self,
        error: Exception | KeyboardInterrupt,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM errors."""
        message = ChatMessage(
            id=run_id,
            conversation=self.conversation_id,
            from_="ai",
            content=f"llm error: {str(error)}",
            type="error",
        )
        await self.websocket.send_text(message.model_dump_json())
