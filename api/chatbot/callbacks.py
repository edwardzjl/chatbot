"""Callback handlers used in the app.
A modified version of langchain.callbacks.AsyncIteratorCallbackHandler.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi import WebSocket
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult

from chatbot.schemas import ChatMessage, Conversation


class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self, websocket: WebSocket, conversation_id: str):
        self.websocket = websocket
        self.conversation_id = conversation_id

    async def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        message = ChatMessage(
            id=run_id, from_=self.conversation_id, content=None, type="start"
        )
        await self.websocket.send_json(message.dict())

    async def on_llm_new_token(
        self,
        token: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        message = ChatMessage(
            id=run_id, from_=self.conversation_id, content=token, type="stream"
        )
        await self.websocket.send_json(message.dict())

    async def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        message = ChatMessage(
            id=run_id, from_=self.conversation_id, content=None, type="end"
        )
        await self.websocket.send_json(message.dict())

    async def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM errors."""
        message = ChatMessage(
            id=run_id,
            from_=self.conversation_id,
            content=f"llm error: {str(error)}",
            type="error",
        )
        await self.websocket.send_json(message.dict())


class UpdateConversationCallbackHandler(AsyncCallbackHandler):
    def __init__(self, conversation_id: str):
        self.conversation_id: str = conversation_id

    async def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain ends running."""
        conv = await Conversation.get(self.conversation_id)
        conv.updated_at = datetime.now()
        await conv.save()
