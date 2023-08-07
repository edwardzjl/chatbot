"""Callback handlers used in the app.
A modified version of langchain.callbacks.AsyncIteratorCallbackHandler.
"""
import asyncio
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Literal, Union, Optional, cast
from uuid import UUID

from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult
from loguru import logger

from chatbot.schemas import StreamResponse, Conversation


class SSEMessageCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses as Server Sent Events."""

    queue: asyncio.Queue[StreamResponse]
    """Queue of stream responses from the LLM."""

    done: asyncio.Event
    """Usually we want to pop all items from the queue, but if we get an error, or we want to do an early stop, we set this event."""

    @property
    def always_verbose(self) -> bool:
        return True

    def __init__(self) -> None:
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()

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
        # If two calls are made in a row, this resets the state
        self.done.clear()

    async def on_llm_new_token(
        self,
        token: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        if token is not None and token != "":
            self.queue.put_nowait(StreamResponse(id=run_id.hex, text=token))

    async def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        self.done.set()

    async def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        logger.error(f"Error from LLM: {error}")
        self.done.set()

    async def aiter(self) -> AsyncIterator[str]:
        while not self.queue.empty() or not self.done.is_set():
            # Wait for the next token in the queue,
            # but stop waiting if the done event is set
            done, other = await asyncio.wait(
                [
                    # NOTE: If you add other tasks here, update the code below,
                    # which assumes each set has exactly one task each
                    asyncio.ensure_future(self.queue.get()),
                    asyncio.ensure_future(self.done.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel the other task
            if other:
                other.pop().cancel()

            # Extract the value of the first completed task
            resp_or_done = cast(
                Union[StreamResponse, Literal[True]], done.pop().result()
            )

            # If the extracted value is the boolean True, the done event was set
            if resp_or_done is True:
                break

            yield resp_or_done.json()


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
