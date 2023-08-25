import asyncio
from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Header, Depends
from langchain.chains import ConversationChain
from langchain.llms import HuggingFaceTextGenInference
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseChatMessageHistory
from sse_starlette.sse import EventSourceResponse

from chatbot.callbacks import (
    SSEMessageCallbackHandler,
    UpdateConversationCallbackHandler,
)
from chatbot.history import AppendSuffixHistory
from chatbot.prompts.vicuna import (
    prompt,
    human_prefix,
    ai_prefix,
    human_suffix,
    ai_suffix,
)
from chatbot.schemas import ConversationDetail, Conversation, UpdateConversation
from chatbot.settings import settings


router = APIRouter(
    prefix="/api",
    tags=["conversation"],
)


def message_history(
    conversation_id: str,
    kubeflow_userid: Annotated[str | None, Header()] = None,
) -> BaseChatMessageHistory:
    return AppendSuffixHistory(
        url=settings.redis_om_url,
        session_id=f"{kubeflow_userid}:{conversation_id}",
        user_suffix=human_suffix,
        ai_suffix=ai_suffix,
    )


@router.get("/conversations", response_model=list[Conversation])
async def get_conversations(kubeflow_userid: Annotated[str | None, Header()] = None):
    convs = await Conversation.find(Conversation.owner == kubeflow_userid).all()
    convs.sort(key=lambda x: x.updated_at, reverse=True)
    return convs


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    message_history: Annotated[BaseChatMessageHistory, Depends(message_history)],
    kubeflow_userid: Annotated[str | None, Header()] = None,
):
    conv = await Conversation.get(conversation_id)
    # TODO: role (or 'type') not serialized
    # pydantic will support serializing @property by @computed_field annotation in v2.0
    # See <https://github.com/pydantic/pydantic/issues/935#issuecomment-1516822249>
    # Since v2.0 is not yet released, we will simply keep this feature on hold.
    return ConversationDetail(
        messages=[
            {
                "from": message.type,
                "content": message.content,
            }
            for message in message_history.messages
        ],
        **conv.dict(),
    )


@router.post("/conversations", status_code=201, response_model=Conversation)
async def create_conversation(kubeflow_userid: Annotated[str | None, Header()] = None):
    conv = Conversation(title=f"conversation at {date.today()}", owner=kubeflow_userid)
    await conv.save()
    return conv


@router.put("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    payload: UpdateConversation,
    kubeflow_userid: Annotated[str | None, Header()] = None,
):
    conv = await Conversation.get(conversation_id)
    conv.title = payload.title
    conv.updated_at = datetime.now()
    await conv.save()


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str, kubeflow_userid: Annotated[str | None, Header()] = None
):
    await Conversation.delete(conversation_id)


@router.post("/conversations/{conversation_id}/messages")
async def generate(
    data: dict,
    message_history: Annotated[BaseChatMessageHistory, Depends(message_history)],
    sse_callback: Annotated[SSEMessageCallbackHandler, Depends()],
    update_conversation_callback: Annotated[
        UpdateConversationCallbackHandler, Depends()
    ],
):
    llm = HuggingFaceTextGenInference(
        inference_server_url=settings.inference_server_url,
        max_new_tokens=1024,
        temperature=0.8,
        top_p=0.9,
        repetition_penalty=1.1,
        stop_sequences=["</s>"],
        streaming=True,
        callbacks=[sse_callback],
    )
    memory = ConversationBufferWindowMemory(
        human_prefix=human_prefix,
        ai_prefix=ai_prefix,
        memory_key="history",
        chat_memory=message_history,
    )
    conversation_chain: ConversationChain = ConversationChain(
        llm=llm,
        prompt=prompt,
        verbose=False,
        memory=memory,
        callbacks=[update_conversation_callback],
    )
    asyncio.create_task(conversation_chain.arun(input=data["message"]))
    return EventSourceResponse(
        sse_callback.aiter(), headers={"content-type": "text/event-stream"}
    )
