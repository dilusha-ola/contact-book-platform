from fastapi import Header, HTTPException, status
from app.core.config import settings

async def verify_api_key(
    x_api_key: str = Header(None, alias="X-API-Key"),
    authorization: str = Header(None, alias="Authorization"),
):
    # 1. MudraID Bearer token (validated by MudraIDMiddleware)
    if authorization and authorization.startswith("Bearer "):
        return

    # 2. Local Browser UI requests (browser doesn't send auth headers)
    if not authorization and not x_api_key:
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized request. Valid MudraID Bearer token or X-API-Key required."
    )

