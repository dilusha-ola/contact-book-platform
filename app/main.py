import os
import logging
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
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
@app.post("/health", summary="Platform Health Check (POST)", tags=["Health"])
async def root_health_check():
    return {"status": "ok", "service": "contact-book-platform"}

@app.post("/", summary="Universal Discovery Probe Handshake", tags=["API Discovery"])
@app.get("/api/v1", summary="Universal Discovery Probe Handshake", tags=["API Discovery"])
@app.post("/api/v1", summary="Universal Discovery Probe Handshake", tags=["API Discovery"])
@app.get("/mcp", summary="MCP Discovery Endpoint", tags=["API Discovery"])
@app.post("/mcp", summary="MCP Discovery Endpoint", tags=["API Discovery"])
@app.get("/api/v1/mcp", summary="MCP API Discovery Endpoint", tags=["API Discovery"])
@app.post("/api/v1/mcp", summary="MCP API Discovery Endpoint", tags=["API Discovery"])
async def universal_discovery_handshake(request: Request):
    """
    Universal Discovery Probe endpoint supporting:
    1. OpenAPI 3.1.0 specification auto-discovery
    2. MCP (Model Context Protocol) JSON-RPC 2.0 (initialize, ping, tools/list)
    """
    # === DEBUG: Log every detail of the incoming probe request ===
    body = await request.body()
    body_text = body.decode("utf-8", errors="replace") if body else "(empty)"
    logger.warning(
        f"🔍 DISCOVERY PROBE RECEIVED:\n"
        f"  HTTP Method: {request.method}\n"
        f"  Path: {request.url.path}\n"
        f"  Full URL: {request.url}\n"
        f"  Headers: {dict(request.headers)}\n"
        f"  Body: {body_text[:2000]}"
    )

    try:
        data = json.loads(body.decode("utf-8")) if body else {}
    except Exception:
        data = {}

    method = data.get("method")
    req_id = data.get("id", 1)

    # 1. Handle MCP JSON-RPC 'initialize' probe
    if method == "initialize":
        # Echo the client's requested protocolVersion for compatibility
        client_protocol = data.get("params", {}).get("protocolVersion", "2025-11-25")
        import uuid
        session_id = str(uuid.uuid4())
        response_body = {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": client_protocol,
                "capabilities": {
                    "tools": {"listChanged": False}
                },
                "serverInfo": {
                    "name": "contact-book-platform",
                    "version": "1.0.0"
                }
            }
        }
        logger.warning(f"🔍 INITIALIZE RESPONSE: {json.dumps(response_body)}")
        return JSONResponse(
            content=response_body,
            headers={"Mcp-Session-Id": session_id}
        )

    # 2. Handle MCP JSON-RPC 'ping' probe
    if method == "ping":
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        })

    # 3. Handle MCP notifications
    if method == "notifications/initialized":
        return JSONResponse(content={"jsonrpc": "2.0"}, status_code=200)

    # 4. Handle MCP JSON-RPC 'tools/list' probe
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "list_contacts",
                        "description": "List and search personal contacts",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Filter by name"},
                                "email": {"type": "string", "description": "Filter by email"},
                                "query": {"type": "string", "description": "General search query"}
                            }
                        }
                    },
                    {
                        "name": "create_contact",
                        "description": "Create a new personal contact",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                                "phone": {"type": "string"},
                                "notes": {"type": "string"}
                            },
                            "required": ["name", "email", "phone"]
                        }
                    },
                    {
                        "name": "update_contact",
                        "description": "Update an existing personal contact by ID",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "contact_id": {"type": "string"},
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                                "phone": {"type": "string"},
                                "notes": {"type": "string"}
                            },
                            "required": ["contact_id"]
                        }
                    },
                    {
                        "name": "delete_contact",
                        "description": "Delete a personal contact by ID",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "contact_id": {"type": "string"}
                            },
                            "required": ["contact_id"]
                        }
                    },
                    {
                        "name": "list_companies",
                        "description": "List and search company contacts",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "company_email": {"type": "string"},
                                "location": {"type": "string"},
                                "query": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "create_company",
                        "description": "Create a new company contact",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "company_email": {"type": "string"},
                                "phone": {"type": "string"},
                                "location": {"type": "string"},
                                "notes": {"type": "string"}
                            },
                            "required": ["name", "company_email", "phone", "location"]
                        }
                    },
                    {
                        "name": "update_company",
                        "description": "Update an existing company contact by ID",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "company_id": {"type": "string"},
                                "name": {"type": "string"},
                                "company_email": {"type": "string"},
                                "phone": {"type": "string"},
                                "location": {"type": "string"},
                                "notes": {"type": "string"}
                            },
                            "required": ["company_id"]
                        }
                    },
                    {
                        "name": "delete_company",
                        "description": "Delete a company contact by ID",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "company_id": {"type": "string"}
                            },
                            "required": ["company_id"]
                        }
                    }
                ]
            }
        }

    # 3. Default to returning the full OpenAPI 3.1.0 schema
    return app.openapi()

# 1. Mount API Router (/api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)

# 2. Static directory resolution
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "static"))

# 3. Smart Root GET Handler: Serves Web UI HTML to browsers, and OpenAPI discovery to MudraID probes
@app.get("/", summary="Root Endpoint (Browser UI & Discovery Probe)", include_in_schema=False)
async def root_get(request: Request):
    accept = request.headers.get("accept", "")
    # If a real browser is loading the website, serve the index.html UI
    if "text/html" in accept:
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    # Otherwise (API client, MudraID discovery probe), return OpenAPI / JSON Discovery Handshake
    return await universal_discovery_handshake(request)

# 4. Mount Static Assets (/css and /js)
css_dir = os.path.join(STATIC_DIR, "css")
js_dir = os.path.join(STATIC_DIR, "js")
if os.path.exists(css_dir):
    app.mount("/css", StaticFiles(directory=css_dir), name="css")
if os.path.exists(js_dir):
    app.mount("/js", StaticFiles(directory=js_dir), name="js")
app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")

