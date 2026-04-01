"""
Keycloak Authentication Middleware
Extracts and validates Keycloak tokens from requests
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from brain.guardrails import SessionManager

logger = logging.getLogger(__name__)


def extract_token_from_header(request: Request) -> Optional[str]:
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return None


def extract_token_from_cookie(request: Request) -> Optional[str]:
    return request.cookies.get("keycloak_token") or request.cookies.get("access_token")


class KeycloakAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and validate Keycloak tokens"""
    
    def __init__(self, app, session_manager: Optional[SessionManager] = None):
        super().__init__(app)
        self.session_manager = session_manager or SessionManager()
        self.public_paths = [
            "/api/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
    
    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)
        
        token = extract_token_from_header(request) or extract_token_from_cookie(request)
        user_context = {}
        
        if token:
            result = self.session_manager.validate_session(token)
            if result["valid"]:
                user_context = result["user_context"]
                # logger.debug(f"Auth success for {user_context.get('user_id')}")
            else:
                logger.info(f"Auth invalid: {result.get('error')}")
        
        request.state.user_context = user_context
        request.state.authenticated = user_context.get("authenticated", False)
        request.state.user_id = user_context.get("user_id", "anonymous")
        request.state.token = token
        
        return await call_next(request)


def get_user_context(request: Request) -> Dict[str, Any]:
    return getattr(request.state, "user_context", {})

def get_user_id(request: Request) -> str:
    return getattr(request.state, "user_id", "anonymous")

def is_authenticated(request: Request) -> bool:
    return getattr(request.state, "authenticated", False)
