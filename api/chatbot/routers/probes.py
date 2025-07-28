import asyncio

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
)

from chatbot.dependencies.commons import SettingsDep
from chatbot.dependencies.db import SqlalchemyEngineDep, SqlalchemyROEngineDep
from chatbot.llm_client import (
    llamacppChatOpenAI,
    TGIChatOpenAI,
    VLLMChatOpenAI,
    GithubChatOpenAI,
)


router = APIRouter()


@router.get("/healthz")
async def healthz_check():
    """Liveness probe endpoint.
    Returns 200 OK if the application process is running.
    This typically does not check external dependencies,
    as a failure here would mean the application needs to be restarted.
    """
    return "OK"


@router.get("/readyz")
async def readyz_check(
    settings: SettingsDep, engine: SqlalchemyEngineDep, ro_engine: SqlalchemyROEngineDep
):
    """Readiness probe endpoint.
    Returns 200 OK if the application is ready to serve traffic.
    This typically checks external dependencies like database connections,
    LLM service connectivity, or other critical services.
    """
    check_tasks = []
    try:
        for llm in settings.llms:
            # These endpoints will be used anyway and the result will be cached.
            if isinstance(llm, llamacppChatOpenAI):
                llm._fetch_server_props()
            elif isinstance(llm, TGIChatOpenAI):
                llm._fetch_server_info()
            elif isinstance(llm, VLLMChatOpenAI):
                llm._fetch_models_meta()
            elif isinstance(llm, GithubChatOpenAI):
                llm._fetch_models_meta()
            else:
                # TODO: check /v1/models endpoint for OpenAI and other LLMs
                pass
        if settings.safety_llm:
            # TODO: check /v1/models endpoint for OpenAI and other LLMs
            pass

        check_tasks.append(_check_db_connection(engine))

        if settings.db_standby_url != settings.db_primary_url:
            check_tasks.append(_check_db_connection(ro_engine))

        # TODO: check other services.

        await asyncio.gather(*check_tasks)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {e}",
        )
    else:
        return "OK"


async def _check_db_connection(engine_or_conn: AsyncConnection | AsyncEngine) -> None:
    """Helper function to check a single database connection."""
    async with engine_or_conn.connect() as conn:
        await conn.execute(text("SELECT 1"))
