from typing_extensions import Self

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.graph import CompiledGraph
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, ConfigDict, model_validator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from chatbot.config import settings
from chatbot.utils import remove_driver


class AppState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    conn_pool: AsyncConnectionPool | None = None
    chat_model: BaseChatModel | None = None
    checkpointer: AsyncPostgresSaver | None = None
    agent: CompiledGraph | None = None
    sqlalchemy_engine: AsyncEngine | None = None
    sqlalchemy_session: sessionmaker | None = None

    @model_validator(mode="after")
    def initialize(self) -> Self:
        # TODO: migrate client pooling to pgbouncer
        # Read more about pool sizing: <https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing>
        self.conn_pool = AsyncConnectionPool(
            remove_driver(str(settings.db_url)),
            open=False,
            min_size=4,
            max_size=10,
            check=AsyncConnectionPool.check_connection,
        )
        self.sqlalchemy_engine = create_async_engine(
            str(settings.db_url),
            async_creator=self.conn_pool.getconn,
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
