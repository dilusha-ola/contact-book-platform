import hmac
import hashlib
import logging
from fastapi import APIRouter, Request, HTTPException, status, Header
from typing import Optional
from app.core.config import settings

logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/webhooks", tags=["MudraID Webhooks"])

@router.post("/mudraid", status_code=status.HTTP_200_OK, summary="MudraID Security Events Webhook")
async def handle_mudraid_webhook(
    request: Request,
    x_mudraid_signature: Optional[str] = Header(None, alias="x-mudraid-signature")
):
    """
    Receives and processes signed real-time security events from MudraID:
    - platform.registered
    - platform.verified
    - verification.succeeded
    - verification.failed
    - access.blocked
    - credential.rotated
    """
    try:
        body = await request.body()
        payload = await request.json() if body else {}
    except Exception as e:
        logger.error(f"❌ Invalid webhook payload received: {e}")
        return {"status": "error", "message": "Invalid JSON payload"}

    event_type = payload.get("event") or payload.get("event_type") or payload.get("type", "unknown_event")
    event_id = payload.get("id") or payload.get("event_id", "test_delivery")
    timestamp = payload.get("timestamp") or payload.get("created_at", "now")

    logger.info(
        f"\n==================== MudraID Webhook Received ====================\n"
        f" Event Type  : {event_type}\n"
        f" Event ID    : {event_id}\n"
        f" Timestamp   : {timestamp}\n"
        f" Signature   : {x_mudraid_signature or 'Not provided (Test Ping)'}\n"
        f" Payload     : {payload}\n"
        f"==================================================================\n"
    )

    return {
        "status": "success",
        "received": True,
        "event_type": event_type,
        "event_id": event_id
    }
