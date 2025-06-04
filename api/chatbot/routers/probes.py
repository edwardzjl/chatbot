from fastapi import APIRouter


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
async def readyz_check():
    """Readiness probe endpoint.
    Returns 200 OK if the application is ready to serve traffic.
    This typically checks external dependencies like database connections,
    LLM service connectivity, or other critical services.
    """
    # TODO: Implement actual readiness checks for external dependencies
    return "OK"
