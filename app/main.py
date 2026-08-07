import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router
from app.db.session import connect_to_mongo, close_mongo_connection
from starlette.middleware.base import BaseHTTPMiddleware
# pyrefly: ignore [missing-import]
from mudraid_middleware import MudraIDMiddleware
from app.core.config import settings

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
        self.mudraid = MudraIDMiddleware(app)

    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/api/"):
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                return await self.mudraid.dispatch(request, call_next)
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

# 1. Mount API Router (/api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)

# 2. Mount Static Web UI (No Jinja2 required)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "static"))

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
