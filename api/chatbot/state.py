"""This module holds some singletons that will be used accoss the app."""

from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from chatbot.config import settings


sqlalchemy_engine = create_async_engine(
    str(settings.db_url),
    poolclass=NullPool,
)
sqlalchemy_session = sessionmaker(
    sqlalchemy_engine,
    autocommit=False,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)
chat_model = ChatOpenAI(
    openai_api_base=str(settings.llm.url),
    model=settings.llm.model,
    openai_api_key=settings.llm.creds,
    max_tokens=1024,
    streaming=True,
)
