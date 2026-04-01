"""
Session Manager for Keycloak Authentication
Handles unified session tracking from login to logout
"""

import logging
import os
import uuid
import jwt
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class UserSession:
    session_id: str
    user_id: str
    login_time: datetime
    last_activity: datetime
    logout_time: Optional[datetime] = None
    status: str = "active"
    token_state: Optional[str] = None
    user_info: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        return self.status == "active" and self.logout_time is None
    
    def end_session(self):
        self.status = "ended"
        self.logout_time = datetime.now()
        logger.info(f"Session {self.session_id} ended user={self.user_id}")
    
    def update_activity(self):
        if self.is_active():
            self.last_activity = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "login_time": self.login_time.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "logout_time": self.logout_time.isoformat() if self.logout_time else None,
            "status": self.status,
            "user_info": self.user_info
        }


class SessionManager:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.keycloak_url = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
        self.keycloak_realm = os.getenv("KEYCLOAK_REALM", "thinklife")
        self.keycloak_client_id = os.getenv("KEYCLOAK_CLIENT_ID", "thinklife-frontend")
        
        self.sessions: Dict[str, UserSession] = {}
        self.user_sessions: Dict[str, list] = {}
        self.token_to_session: Dict[str, str] = {}
        
        self.public_key_cache = {}
        self.public_key_cache_expiry = {}
        
        logger.info("SessionManager initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "token_validation": {"enabled": True, "verify_signature": True},
            "session_timeout": {"enabled": True, "max_hours": 24},
            "user_context": {"include_roles": True, "include_email": True, "include_profile": True}
        }
    
    @lru_cache(maxsize=1)
    def _get_public_key(self) -> Optional[str]:
        try:
            cache_key = f"{self.keycloak_url}/{self.keycloak_realm}"
            if cache_key in self.public_key_cache:
                if datetime.now() < self.public_key_cache_expiry.get(cache_key, datetime.min):
                    return self.public_key_cache[cache_key]
            
            url = f"{self.keycloak_url}/realms/{self.keycloak_realm}"
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            
            key = resp.json().get("public_key")
            if key:
                self.public_key_cache[cache_key] = key
                self.public_key_cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)
                return key
            return None
        except Exception:
            logger.warning("Failed to fetch Keycloak public key", exc_info=True)
            return None
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        if not token: return {"valid": False, "error": "No token"}
        
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            issuer = unverified.get("iss")
            expected = f"{self.keycloak_url}/realms/{self.keycloak_realm}"
            
            if issuer != expected:
                return {"valid": False, "error": f"Invalid issuer: {issuer}"}
            
            key = self._get_public_key()
            if not key:
                logger.warning("Verifying without signature (key missing)")
                decoded = jwt.decode(token, options={"verify_signature": False, "verify_exp": True})
            else:
                decoded = jwt.decode(
                    token,
                    f"-----BEGIN PUBLIC KEY-----\n{key}\n-----END PUBLIC KEY-----",
                    algorithms=["RS256"],
                    issuer=expected,
                    options={"verify_exp": True}
                )
            
            info = {
                "user_id": decoded.get("sub"),
                "email": decoded.get("email"),
                "name": decoded.get("name"),
                "roles": decoded.get("realm_access", {}).get("roles", []),
                "session_state": decoded.get("session_state")
            }
            return {"valid": True, "user": info}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def create_session(self, token: str, user_info: Optional[Dict] = None) -> Dict[str, Any]:
        if not user_info:
            val = self.validate_token(token)
            if not val["valid"]: return {"success": False, "error": val["error"]}
            user_info = val["user"]
        
        uid = user_info.get("user_id")
        state = user_info.get("session_state")
        if not uid: return {"success": False, "error": "No user ID"}
        
        # Check existing
        if state and state in self.token_to_session:
            sid = self.token_to_session[state]
            sess = self.sessions.get(sid)
            if sess and sess.is_active():
                sess.update_activity()
                return {"success": True, "session_id": sid, "user_context": self.create_user_context(user_info, sid)}
        
        # New
        sid = str(uuid.uuid4())
        now = datetime.now()
        session = UserSession(sid, uid, now, now, token_state=state, user_info=user_info)
        
        self.sessions[sid] = session
        if uid not in self.user_sessions: self.user_sessions[uid] = []
        self.user_sessions[uid].append(sid)
        if state: self.token_to_session[state] = sid
        
        logger.info(f"New session {sid} user={uid}")
        return {"success": True, "session_id": sid, "user_context": self.create_user_context(user_info, sid)}
    
    def end_session(self, session_id: str = None, user_id: str = None, token_state: str = None) -> bool:
        if session_id:
            sess = self.sessions.get(session_id)
            if sess and sess.is_active():
                sess.end_session()
                if sess.token_state in self.token_to_session: del self.token_to_session[sess.token_state]
                return True
        elif token_state:
            return self.end_session(session_id=self.token_to_session.get(token_state))
        elif user_id:
            sids = self.get_user_active_sessions(user_id)
            for sid in sids: self.end_session(session_id=sid)
            return bool(sids)
        return False
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        return self.sessions.get(session_id)
    
    def validate_session(self, token: str = None, user_context: Dict = None) -> Dict[str, Any]:
        if not token and user_context:
            sid = user_context.get("session_id")
            sess = self.sessions.get(sid)
            if sess and sess.is_active():
                sess.update_activity()
                return {"valid": True, "user_context": user_context}
            return {"valid": False, "error": "No valid session"}
        
        if not token: return {"valid": False, "error": "No token"}
        
        val = self.validate_token(token)
        if not val["valid"]: return {"valid": False, "error": val["error"]}
        
        user_info = val["user"]
        state = user_info.get("session_state")
        
        sid = self.token_to_session.get(state) if state else None
        if not sid or not self.sessions.get(sid, UserSession("", "", datetime.min, datetime.min)).is_active():
            res = self.create_session(token, user_info)
            if not res["success"]: return {"valid": False, "error": res["error"]}
            sid = res["session_id"]
            ctx = res["user_context"]
        else:
            ctx = self.create_user_context(user_info, sid)
            
        return {"valid": True, "user_context": ctx}
        
    def create_user_context(self, info: Dict, sid: str) -> Dict:
        return {
            "user_id": info.get("user_id", "anonymous"),
            "session_id": sid,
            "is_authenticated": True,
            "authenticated": True,
            "email": info.get("email"),
            "name": info.get("name"),
            "roles": info.get("roles", [])
        }

    def get_user_active_sessions(self, uid: str) -> list:
        return [sid for sid in self.user_sessions.get(uid, []) if self.sessions[sid].is_active()]
    
    def get_user_sessions(self, uid: str, include_ended: bool = False) -> list:
        sids = self.user_sessions.get(uid, [])
        return [self.sessions[sid].to_dict() for sid in sids if sid in self.sessions and (include_ended or self.sessions[sid].is_active())]
    
    def get_session_stats(self) -> Dict:
        active = sum(1 for s in self.sessions.values() if s.is_active())
        return {"total": len(self.sessions), "active": active, "ended": len(self.sessions) - active}
