import os
import logging
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.v1.router import api_router
from app.db.session import connect_to_mongo, close_mongo_connection
from app.core.config import settings

# pyrefly: ignore [missing-import]
from mudraid_platform_middleware import MudraIDMiddleware

logger = logging.getLogger("uvicorn")

TROUBLESHOOTING_MAP_PLATFORM = {
    "WRONG_AUDIENCE": {
        "meaning": "Your YAML's platform_id doesn't match what MudraID issued.",
        "fix": "Re-export mudraid_scopes.yaml from the portal and redeploy."
    },
    "MIDDLEWARE_NOT_READY": {
        "meaning": "The YAML couldn't be loaded or parsed.",
        "fix": "Fix the scopes.yaml file; the next request recovers without a restart."
    },
    "JWKS_UNAVAILABLE": {
        "meaning": "The middleware couldn't reach MudraID's keys.",
        "fix": "Transient network issue to MudraID; check connectivity."
    },
    "ROUTE_NOT_FOUND": {
        "meaning": "It has no rule in the YAML, or is marked skip.",
        "fix": "Add a rule for it in mudraid_scopes.yaml."
    },
    "MISSING_TOKEN": {
        "meaning": "Authorization header missing or not in 'Bearer <token>' form.",
        "fix": "Ensure requests from MudraID Agent carry a valid Bearer token."
    },
    "MISSING_SCOPE": {
        "meaning": "Token lacks the required scope for this route.",
        "fix": "Request/grant the required scope for the agent in MudraID portal."
    }
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event: Connect to MongoDB Atlas
    await connect_to_mongo()
    yield
    # Shutdown event: Close MongoDB connection
    await close_mongo_connection()

# Scopes MudraID validation to requests carrying a Bearer token (Bot Agent calls).
# Browser UI calls without Bearer tokens pass directly to normal route handlers.
class ScopedMudraIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        jwks_url = settings.MUDRAID_JWKS_URL or os.environ.get("MUDRAID_JWKS_URL") or "https://api.staging.mudraid.ai/.well-known/jwks.json"
        logger.info(f"Initializing MudraIDMiddleware with JWKS URL: {jwks_url}")
        self.mudraid = MudraIDMiddleware(app, jwks_url=jwks_url)

    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/api/"):
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                response = await self.mudraid.dispatch(request, call_next)

                if response.status_code >= 400:
                    body = getattr(response, "body", b"")
                    error_code = "UNKNOWN_ERROR"
                    message = "An error occurred"
                    try:
                        data = json.loads(body.decode("utf-8"))
                        error_code = data.get("error_code", "UNKNOWN_ERROR")
                        message = data.get("message", body.decode("utf-8"))
                    except Exception:
                        message = body.decode("utf-8") if isinstance(body, bytes) else str(body)

                    info = TROUBLESHOOTING_MAP_PLATFORM.get(error_code, {
                        "meaning": message,
                        "fix": "Check platform configuration and MudraID Portal settings."
                    })

                    logger.error(
                        f"\n==================== MudraID Platform Error ====================\n"
                        f" Request Path: {request.method} {request.url.path}\n"
                        f" Status Code : {response.status_code}\n"
                        f" Error Code  : {error_code}\n"
                        f" What it means: {info['meaning']}\n"
                        f" How to fix  : {info['fix']}\n"
                        f"=================================================================\n"
                    )

                    return JSONResponse(
                        status_code=response.status_code,
                        content={
                            "error_code": error_code,
                            "message": message,
                            "what_it_means": info["meaning"],
                            "fix": info["fix"]
                        }
                    )

                return response
        return await call_next(request)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Contact Book Platform RESTful APIs powered by MongoDB Atlas.",
    version="1.0.0",
    lifespan=lifespan
)

# Enforce MudraID authorization on Bot Agent calls
app.add_middleware(ScopedMudraIDMiddleware)

# Enable CORS for local testing & Agent Bot integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", summary="Platform Health Check", tags=["Health"])
async def root_health_check():
    return {"status": "ok", "service": "contact-book-platform"}

# 1. Mount API Router (/api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)

# 2. Mount Static Web UI (No Jinja2 required)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "static"))

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
