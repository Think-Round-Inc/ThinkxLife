"""
Guardrails and security specifications
"""

from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class SecurityConfig:
    """Security configuration"""
    rate_limiting: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "max_requests_per_minute": 60,
        "max_requests_per_hour": 1000
    })
    content_filtering: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "blocked_words": [],
        "trauma_safe_mode": True
    })
    user_validation: Dict[str, Any] = field(default_factory=lambda: {
        "require_auth": True,
        "allow_anonymous": False
    })

