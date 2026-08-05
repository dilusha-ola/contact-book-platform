from fastapi import Header, HTTPException, status
from app.core.config import settings

async def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    if not settings.API_KEY:
        return
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header. Unauthorized request."
        )
