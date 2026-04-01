"""
Zoe Helpers - Utility functions for creating Brain requests
"""

from typing import Dict, Any, Optional
from brain.specs import UserContext, UserProfile, TraumaContext, ApplicationType


def create_user_context(
    user_id: str,
    session_id: str,
    user_context: Optional[Dict[str, Any]] = None
) -> UserContext:
    """
    Create UserContext from user data
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        user_context: Optional user context dict with ace_score, etc.
    
    Returns:
        UserContext object for BrainRequest
    """
    user_profile = None
    trauma_context = None
    
    if user_context and user_context.get("ace_score") is not None:
        user_profile = UserProfile(
            id=user_id,
            ace_score=user_context.get("ace_score", 0.0),
            name=None,
            email=None,
            age=None
        )
        trauma_context = TraumaContext(
            ace_score=user_context.get("ace_score", 0.0),
            trauma_types=[],
            trigger_words=[],
            safety_preferences={},
            healing_goals=[]
        )
    
    return UserContext(
        user_id=user_id,
        session_id=session_id,
        is_authenticated=True,
        user_profile=user_profile,
        trauma_context=trauma_context
    )

