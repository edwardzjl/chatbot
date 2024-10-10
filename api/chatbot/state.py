from typing_extensions import Self

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict, model_validator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from chatbot.config import settings


class AppState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    chat_model: BaseChatModel | None = None
    sqlalchemy_engine: AsyncEngine | None = None
    sqlalchemy_session: sessionmaker | None = None

    @model_validator(mode="after")
    def initialize(self) -> Self:
        self.sqlalchemy_engine = create_async_engine(
            str(settings.db_url),
            poolclass=NullPool,
        )
        self.sqlalchemy_session = sessionmaker(
            self.sqlalchemy_engine,
            autocommit=False,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )

        self.chat_model = ChatOpenAI(
            openai_api_base=str(settings.llm.url),
            model=settings.llm.model,
            openai_api_key=settings.llm.creds,
            max_tokens=1024,
            streaming=True,
        )


app_state = AppState()
