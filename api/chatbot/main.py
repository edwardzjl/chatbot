"""Main entrypoint for the app."""
import asyncio
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Annotated

from aredis_om import Migrator, NotFoundError
from fastapi import FastAPI, Header, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import langchain
from langchain.cache import RedisCache
from langchain.chains import ConversationChain
from langchain.llms import HuggingFaceTextGenInference
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.schema import BaseChatMessageHistory
from redis import Redis
from sse_starlette.sse import EventSourceResponse

from chatbot.callbacks import (
    SSEMessageCallbackHandler,
    UpdateConversationCallbackHandler,
)
from chatbot.history import AppendSuffixHistory
from chatbot.prompts.baichuan import (
    prompt,
    human_prefix,
    ai_prefix,
    human_suffix,
    ai_suffix,
)
from chatbot.schemas import ConversationDetail, Conversation, UpdateConversation
from chatbot.settings import settings


# TODO: should separate redis cache and om instance
langchain.llm_cache = RedisCache(redis_=Redis.from_url(settings.redis_om_url))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Migrator().run()
    yield


app = FastAPI(lifespan=lifespan)


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


@app.get("/api/userinfo")
def userinfo(kubeflow_userid: Annotated[str | None, Header()] = None):
    return {"username": kubeflow_userid}


@app.get("/api/conversations", response_model=list[Conversation])
async def get_conversations(kubeflow_userid: Annotated[str | None, Header()] = None):
    convs_iter = await Conversation.find(Conversation.owner == kubeflow_userid)
    if not convs_iter:
        return []
    convs = convs_iter.all()
    convs.sort(key=lambda x: x.updated_at, reverse=True)
    return convs


@app.get("/api/conversations/{conversation_id}", response_model=ConversationDetail)
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


@app.post("/api/conversations", status_code=201, response_model=Conversation)
async def create_conversation(kubeflow_userid: Annotated[str | None, Header()] = None):
    conv = Conversation(title=f"conversation at {date.today()}", owner=kubeflow_userid)
    await conv.save()
    return conv


@app.put("/api/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    payload: UpdateConversation,
    kubeflow_userid: Annotated[str | None, Header()] = None,
):
    conv = await Conversation.get(conversation_id)
    conv.title = payload.title
    conv.updated_at = datetime.now()
    await conv.save()


@app.delete("/api/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str, kubeflow_userid: Annotated[str | None, Header()] = None
):
    await Conversation.delete(conversation_id)


@app.post("/api/conversations/{conversation_id}/messages")
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
        stop_sequences=["</s>", " <reserved_102> "],
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


@app.exception_handler(NotFoundError)
async def notfound_exception_handler(request: Request, exc: NotFoundError):
    # TODO: add some details here
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"detail": str(exc)}),
    )


app.mount(
    "/", StaticFiles(directory="static", html=True, check_dir=False), name="static"
)
