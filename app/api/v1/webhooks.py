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


@router.post("/delivery-destination", status_code=status.HTTP_200_OK, summary="MudraID Delivery Destination Webhook")
async def handle_delivery_destination_webhook(
    request: Request,
    x_mudraid_signature: Optional[str] = Header(None, alias="x-mudraid-signature")
):
    """
    Dedicated receiver endpoint for MudraID Delivery Destinations (Journey J14).
    Receives and logs outbound evidence, audit records, and containment events.
    """
    try:
        body = await request.body()
        payload = await request.json() if body else {}
    except Exception as e:
        logger.error(f"❌ Invalid delivery destination payload received: {e}")
        return {"status": "error", "message": "Invalid JSON payload"}

    # Verify HMAC signature if MUDRAID_DELIVERY_DESTINATION_SECRET is configured
    is_valid_sig = None
    if settings.MUDRAID_DELIVERY_DESTINATION_SECRET and x_mudraid_signature:
        try:
            expected_sig = hmac.new(
                settings.MUDRAID_DELIVERY_DESTINATION_SECRET.encode("utf-8"),
                body,
                hashlib.sha256
            ).hexdigest()
            is_valid_sig = hmac.compare_digest(expected_sig, x_mudraid_signature)
        except Exception as sig_err:
            logger.warning(f"⚠️ Signature check encountered error: {sig_err}")

    event_type = payload.get("event") or payload.get("event_type") or payload.get("type", "test_ping_or_evidence")
    event_id = payload.get("id") or payload.get("event_id", "delivery_probe")
    timestamp = payload.get("timestamp") or payload.get("created_at", "now")

    sig_status_str = "Not Checked (No Secret Configured)"
    if is_valid_sig is True:
        sig_status_str = "✅ Valid HMAC Signature"
    elif is_valid_sig is False:
        sig_status_str = "❌ Signature Mismatch"

    logger.info(
        f"\n================ MudraID Delivery Destination Webhook ================\n"
        f" Endpoint    : /api/v1/webhooks/delivery-destination\n"
        f" Event Type  : {event_type}\n"
        f" Event ID    : {event_id}\n"
        f" Timestamp   : {timestamp}\n"
        f" Signature   : {x_mudraid_signature or 'None (Test Ping)'}\n"
        f" Sig Status  : {sig_status_str}\n"
        f" Payload     : {payload}\n"
        f"======================================================================\n"
    )

    return {
        "status": "success",
        "received": True,
        "destination_event": event_type,
        "event_id": event_id,
        "signature_valid": is_valid_sig
    }
