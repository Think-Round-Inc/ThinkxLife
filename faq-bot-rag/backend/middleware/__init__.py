"""
Middleware module for ThinkLife Backend
"""

from .keycloak_auth import (
    KeycloakAuthMiddleware,
    get_user_context,
    get_user_id,
    is_authenticated,
    extract_token_from_header,
    extract_token_from_cookie,
)

__all__ = [
    "KeycloakAuthMiddleware",
    "get_user_context",
    "get_user_id",
    "is_authenticated",
    "extract_token_from_header",
    "extract_token_from_cookie",
]

