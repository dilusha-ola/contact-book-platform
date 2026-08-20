from fastapi import APIRouter
from app.api.v1 import contacts, companies, webhooks

api_router = APIRouter()

@api_router.get("", summary="API v1 Base Endpoint", tags=["API Discovery"])
@api_router.get("/", summary="API v1 Base Endpoint", tags=["API Discovery"])
@api_router.post("", summary="API v1 Discovery Probe Handshake", tags=["API Discovery"])
@api_router.post("/", summary="API v1 Discovery Probe Handshake", tags=["API Discovery"])
async def api_v1_discovery_handshake():
    return {
        "status": "ok",
        "service": "contact-book-platform",
        "version": "1.0.0",
        "discovery": "ready",
        "endpoints": {
            "contacts": "/api/v1/contacts",
            "companies": "/api/v1/companies",
            "webhooks": "/api/v1/webhooks/mudraid"
        }
    }

@api_router.get("/health", summary="API Health Check", tags=["Health"])
async def api_v1_health():
    return {"status": "ok", "service": "contact-book-platform", "health": "healthy"}

api_router.include_router(contacts.router)
api_router.include_router(companies.router)
api_router.include_router(webhooks.router)


