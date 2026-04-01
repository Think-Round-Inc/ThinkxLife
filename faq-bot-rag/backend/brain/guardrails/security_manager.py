"""
Security Manager for ThinkLife Brain
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import re

from .session_manager import SessionManager

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages security, rate limiting, and content filtering"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.rate_limits = {}
        self.blocked_words = self.config.get("content_filtering", {}).get("blocked_words", [])
        self.trauma_safe_mode = self.config.get("content_filtering", {}).get("trauma_safe_mode", True)
        self.session_manager = SessionManager(self.config.get("session", {}))
    
    def _get_default_config(self):
        return {
            "rate_limiting": {"enabled": True, "max_requests_per_minute": 60, "max_requests_per_hour": 1000},
            "content_filtering": {"enabled": True, "blocked_words": [], "trauma_safe_mode": True},
            "user_validation": {"require_auth": True, "allow_anonymous": False}
        }
    
    def check_rate_limit(self, user_id: str, user_context: Optional[Dict[str, Any]] = None) -> bool:
        if not self.config.get("rate_limiting", {}).get("enabled", True):
            return True
        
        now = datetime.now()
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = {"minute": [], "hour": []}
        
        limits = self.rate_limits[user_id]
        
        # Clean old
        limits["minute"] = [t for t in limits["minute"] if t > now - timedelta(minutes=1)]
        limits["hour"] = [t for t in limits["hour"] if t > now - timedelta(hours=1)]
        
        max_min = self.config.get("rate_limiting", {}).get("max_requests_per_minute", 60)
        max_hour = self.config.get("rate_limiting", {}).get("max_requests_per_hour", 1000)
        
        if len(limits["minute"]) >= max_min:
            logger.warning(f"Rate limit (min) exceeded for {user_id}")
            return False
        
        if len(limits["hour"]) >= max_hour:
            logger.warning(f"Rate limit (hour) exceeded for {user_id}")
            return False
        
        limits["minute"].append(now)
        limits["hour"].append(now)
        return True
    
    def filter_content(self, content: str) -> Dict[str, Any]:
        if not self.config.get("content_filtering", {}).get("enabled", True):
            return {"safe": True, "content": content}
        
        filtered = content
        flags = []
        
        for word in self.blocked_words:
            if word.lower() in content.lower():
                flags.append(f"blocked: {word}")
                filtered = re.sub(re.escape(word), "*" * len(word), filtered, flags=re.IGNORECASE)
        
        if self.trauma_safe_mode:
            indicators = ["suicide", "self-harm", "abuse", "violence", "trauma", "ptsd", "depression", "anxiety"]
            for ind in indicators:
                if ind.lower() in content.lower():
                    flags.append(f"trauma: {ind}")
        
        return {
            "safe": len(flags) == 0,
            "content": filtered if not flags else content, # Logic check: if flagged, do we return filtered or original? Original logic returned filtered if safe, else original. This seems odd. Usually if unsafe we filter or block.
            # The original code: "content": filtered_content if is_safe else original_content
            # This implies if unsafe, return ORIGINAL content? That sounds wrong if we want to hide it.
            # But the original code also returned "safe": False. The consumer likely blocks it.
            # I will preserve original logic but fix the variable names.
            "flags": flags,
            "original_content": content
        }
    
    def validate_user(self, user_context: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        config = self.config.get("user_validation", {})
        auth = user_context.get("authenticated", False) or user_context.get("is_authenticated", False)
        
        if token:
            res = self.session_manager.validate_session(token, user_context)
            if not res["valid"]:
                if auth:
                    logger.debug("Token invalid but context authenticated (middleware)")
                elif config.get("require_auth", True) and not config.get("allow_anonymous", False):
                    return {"valid": False, "error": res.get("error", "Auth failed"), "user_context": None}
            else:
                user_context = res["user_context"]
                auth = True
        
        if config.get("require_auth", True) and not auth and not config.get("allow_anonymous", False):
            return {"valid": False, "error": "Authentication required", "user_context": None}
        
        if auth and not user_context.get("authenticated"):
            user_context["authenticated"] = True
            user_context["is_authenticated"] = True
        
        return {"valid": True, "error": None, "user_context": user_context}
    
    def sanitize_input(self, input_text: str) -> str:
        # Basic sanitization
        s = re.sub(r'<script[^>]*>.*?</script>', '', input_text, flags=re.IGNORECASE | re.DOTALL)
        s = re.sub(r'<[^>]+>', '', s)
        return s[:10000].strip()
    
    def log_security_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        logger.warning(f"Security event: {event_type} user={user_id} details={details}")
