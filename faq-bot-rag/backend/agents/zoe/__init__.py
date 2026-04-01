"""
Zoe - AI Companion for ThinkLife

Trauma-informed empathetic AI companion with centralized LLM processing.

Architecture:
    Frontend - ZoeService - ZoeAgent (plugin) - CortexFlow - WorkflowEngine - Provider

Components:
    - ZoeCore: Domain logic (personality, prompts, safety, conversation management)
    - ZoeService: Frontend interface (recommended for API/frontend use)
    - ZoePersonality: Trauma-informed personality system
    - ZoeConversationManager: Session and conversation management
    - helpers: Utility functions for creating Brain requests

Usage:
    from agents.zoe import ZoeService
    
    service = ZoeService()
    await service.initialize()
    
    response = await service.process_message(
        message="I'm feeling anxious",
        user_id="user_123",
        user_context={"ace_score": 5}
    )
"""

from .zoe_core import ZoeCore
from .zoe_service import ZoeService, get_zoe_service
from .personality import ZoePersonality
from .conversation_manager import ZoeConversationManager

__all__ = [
    "ZoeService",
    "get_zoe_service",
    "ZoeCore",
    "ZoePersonality",
    "ZoeConversationManager",
] 