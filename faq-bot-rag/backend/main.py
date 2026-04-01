"""
ThinkLife Backend with Brain Integration
This is the main FastAPI application that integrates the ThinkLife Brain
system with existing chatbot functionality.
"""

import logging
import os
import sys
import warnings
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional

# patch for Python < 3.10 to support packages_distributions
# This fixes compatibility issues with google-api-core and other libs on Python 3.9
if sys.version_info < (3, 10):
    try:
        import importlib.metadata
        import importlib_metadata
        if not hasattr(importlib.metadata, "packages_distributions"):
            importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
    except ImportError:
        pass

# Suppress Google API Core Python 3.9 EOL warning
warnings.filterwarnings("ignore", message="You are using a Python version.*past its end of life", category=FutureWarning, module="google.api_core")

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load env
load_dotenv()

logger = logging.getLogger(__name__)

# Imports
from brain import CortexFlow
from agents.zoe import ZoeService
from agents.zoe.tts_service import tts_service
from middleware.keycloak_auth import KeycloakAuthMiddleware, get_user_context, extract_token_from_header, extract_token_from_cookie, get_user_id
from brain.guardrails import SessionManager

# Global instances
brain_instance = None
zoe_service_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global brain_instance, zoe_service_instance

    logger.info("Starting ThinkLife Backend...")

    # Brain Config
    brain_config = {
        "providers": {
            "openai": {
                "enabled": bool(os.getenv("OPENAI_API_KEY")),
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
                "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            }
        }
    }

    brain_instance = CortexFlow(brain_config)
    await brain_instance.initialize()
    logger.info("CortexFlow initialized")

    zoe_service_instance = ZoeService()
    await zoe_service_instance.initialize()
    logger.info("ZoeService initialized")

    yield

    logger.info("Shutting down...")
    if brain_instance: await brain_instance.shutdown()
    if zoe_service_instance: await zoe_service_instance.shutdown()
    logger.info("Shutdown complete")


app = FastAPI(
    title="ThinkLife Backend with Brain",
    description="AI-powered backend with centralized Brain orchestration",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://thinklife.vercel.app",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(KeycloakAuthMiddleware)


# Models
class APIBrainRequest(BaseModel):
    message: str
    application: str
    user_context: Dict[str, Any] = {}
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class APIBrainResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    brain_status: Dict[str, Any]
    timestamp: str


# Dependencies
def get_brain() -> CortexFlow:
    if not brain_instance: raise HTTPException(503, "Brain not initialized")
    return brain_instance

def get_zoe() -> ZoeService:
    if not zoe_service_instance: raise HTTPException(503, "Zoe not initialized")
    return zoe_service_instance


# Brain API
@app.post("/api/brain", response_model=APIBrainResponse)
async def process_brain_request(
    request: APIBrainRequest, 
    brain: CortexFlow = Depends(get_brain),
    http_request: Request = None
):
    try:
        valid_apps = ["healing-rooms", "inside-our-ai", "chatbot", "compliance", "exterior-spaces", "general"]
        if request.application not in valid_apps:
            raise HTTPException(400, f"Invalid app. Must be: {valid_apps}")

        kc_context = get_user_context(http_request) if http_request else {}
        token = extract_token_from_header(http_request) or extract_token_from_cookie(http_request) if http_request else None
        
        merged_context = {**request.user_context, **kc_context}
        metadata = request.metadata or {}
        if token: metadata["token"] = token
        
        data = {
            "id": request.session_id,
            "message": request.message,
            "application": request.application,
            "user_context": merged_context,
            "metadata": metadata,
        }

        res = await brain.process_request(data)

        return APIBrainResponse(
            success=res.get("success", False),
            message=res.get("message"),
            data=res.get("data"),
            error=res.get("error"),
            metadata=res.get("metadata"),
            timestamp=res.get("timestamp", datetime.now().isoformat()),
        )

    except Exception as e:
        logger.exception("Error processing Brain request")
        raise HTTPException(500, str(e))


@app.get("/api/brain/health", response_model=HealthResponse)
async def get_brain_health(brain: CortexFlow = Depends(get_brain)):
    try:
        status = await brain.get_health_status()
        return HealthResponse(
            status=status.get("overall", "unknown"),
            brain_status=status,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(500, str(e))


@app.get("/api/brain/analytics")
async def get_brain_analytics(brain: CortexFlow = Depends(get_brain)):
    try:
        return {
            "success": True,
            "data": await brain.get_analytics(),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(500, str(e))


# Session API
@app.post("/api/session/logout")
async def logout_session(http_request: Request, session_id: Optional[str] = None):
    try:
        ctx = get_user_context(http_request)
        manager = SessionManager()
        
        sid = session_id or ctx.get("session_id")
        uid = ctx.get("user_id")
        
        token = getattr(http_request.state, "token", None)
        state = None
        if token:
            try:
                import jwt
                state = jwt.decode(token, options={"verify_signature": False}).get("session_state")
            except: pass
        
        success = manager.end_session(session_id=sid, user_id=uid if not sid else None, token_state=state if not sid else None)
        
        return {
            "success": success,
            "message": "Session ended" if success else "Session not found",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(500, str(e))


@app.get("/api/session/stats")
async def get_session_stats():
    return {"success": True, "data": SessionManager().get_session_stats(), "timestamp": datetime.now().isoformat()}


@app.get("/api/session/user/{user_id}")
async def get_user_sessions(user_id: str, include_ended: bool = False):
    try:
        sessions = SessionManager().get_user_sessions(user_id, include_ended=include_ended)
        return {"success": True, "data": {"user_id": user_id, "sessions": sessions, "count": len(sessions)}, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        raise HTTPException(500, str(e))


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    session = SessionManager().get_session(session_id)
    if not session: raise HTTPException(404, "Session not found")
    return {"success": True, "data": session.to_dict(), "timestamp": datetime.now().isoformat()}


# Zoe API
@app.post("/api/zoe/chat")
async def zoe_chat_endpoint(
    request: Dict[str, Any], 
    zoe: ZoeService = Depends(get_zoe),
    http_request: Request = None
):
    try:
        kc_context = get_user_context(http_request) if http_request else {}
        kc_uid = get_user_id(http_request) if http_request else None
        
        msg = request.get("message", "")
        uid = kc_uid or request.get("user_id", "anonymous")
        sid = request.get("session_id")
        ctx = {**request.get("user_context", {}), **kc_context}

        if ctx.get("ace_score", 0) >= 4:
            raise HTTPException(403, "Chat restricted due to ACE score safety policy.")

        if not msg.strip(): raise HTTPException(400, "Message empty")
        if len(msg) > 10000: raise HTTPException(400, "Message too long")

        return await zoe.process_message(
            message=msg, user_id=uid, session_id=sid, user_context=ctx, application="chatbot"
        )
    except Exception as e:
        logger.exception("Zoe chat error")
        raise HTTPException(500, str(e))


@app.get("/api/zoe/sessions/{session_id}/history")
async def get_zoe_session_history(session_id: str, zoe: ZoeService = Depends(get_zoe)):
    return {
        "success": True, 
        "history": zoe.get_conversation_history(session_id),
        "session_id": session_id,
        "timestamp": datetime.now().isoformat()
    }


@app.delete("/api/zoe/sessions/{session_id}")
async def end_zoe_session(session_id: str, zoe: ZoeService = Depends(get_zoe)):
    zoe.clear_conversation(session_id)
    return {"success": True, "message": "History cleared", "session_id": session_id, "timestamp": datetime.now().isoformat()}


@app.get("/api/zoe/health")
async def get_zoe_health(zoe: ZoeService = Depends(get_zoe)):
    return await zoe.health_check()


# Legacy / App Endpoints
@app.post("/api/chat")
async def legacy_chat_endpoint(request: Dict[str, Any], zoe: ZoeService = Depends(get_zoe)):
    try:
        msg = request.get("message", "")
        uid = request.get("user_id", "anonymous")
        sid = request.get("session_id")
        ctx = request.get("user_context", {})

        if ctx.get("ace_score", 0) >= 4:
            return {"success": False, "error": "ACE score restriction", "restricted": True}

        if not msg.strip(): return {"success": False, "error": "No message"}
        
        res = await zoe.process_message(msg, uid, sid, ctx, "chatbot")
        
        audio = None
        if (ctx.get("avatar_mode") or ctx.get("test_tts")) and res.get("success"):
            audio = await tts_service.generate_speech(res.get("response", ""))
            
        return {
            "response": res.get("response", ""),
            "success": res.get("success", False),
            "error": res.get("error"),
            "session_id": res.get("session_id"),
            "audio_data": audio,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.exception("Legacy chat error")
        return {"success": False, "error": str(e), "response": "Technical error"}


# Generic App Handlers
@app.post("/api/{app_name}")
async def generic_app_endpoint(app_name: str, request: Dict[str, Any], brain: CortexFlow = Depends(get_brain)):
    # Validate app_name against allowed list if needed, or let Brain handle it
    req = APIBrainRequest(
        message=request.get("message", ""),
        application=app_name,
        user_context=request.get("user_context", {}),
        session_id=request.get("session_id"),
        metadata=request.get("metadata", {})
    )
    return await process_brain_request(req, brain)

# Explicit mappings for backward compatibility
@app.post("/api/healing-rooms")
async def healing_rooms(r: Dict[str, Any], b: CortexFlow = Depends(get_brain)): return await generic_app_endpoint("healing-rooms", r, b)

@app.post("/api/inside-our-ai")
async def inside_ai(r: Dict[str, Any], b: CortexFlow = Depends(get_brain)): return await generic_app_endpoint("inside-our-ai", r, b)

@app.post("/api/compliance")
async def compliance(r: Dict[str, Any], b: CortexFlow = Depends(get_brain)): return await generic_app_endpoint("compliance", r, b)

@app.post("/api/exterior-spaces")
async def exterior(r: Dict[str, Any], b: CortexFlow = Depends(get_brain)): return await generic_app_endpoint("exterior-spaces", r, b)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "brain": brain_instance is not None,
        "zoe": zoe_service_instance is not None
    }

@app.get("/")
async def root():
    return {"message": "ThinkLife Backend", "version": "0.7.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
