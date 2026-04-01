"""
Core specifications - Brain request/response, user context, configuration, analytics
"""

from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ApplicationType(str, Enum):
    """Available application types"""
    HEALING_ROOMS = "healing-rooms"
    AI_AWARENESS = "inside-our-ai"
    CHATBOT = "chatbot"
    COMPLIANCE = "compliance"
    EXTERIOR_SPACES = "exterior-spaces"
    GENERAL = "general"


class MessageRole(str, Enum):
    """Message roles in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class BrainConfig:
    """Brain configuration"""
    providers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    security: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    session: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Chat message"""
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UserProfile:
    """User profile information"""
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    ace_score: Optional[float] = None
    ai_knowledge_level: Optional[Literal["beginner", "intermediate", "advanced"]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class UserPreferences:
    """User preferences"""
    language: str = "en"
    theme: Literal["light", "dark"] = "light"
    communication_style: Literal["formal", "casual", "empathetic"] = "empathetic"
    ai_personality: Literal["supportive", "educational", "professional"] = "supportive"
    privacy_level: Literal["high", "medium", "low"] = "medium"
    content_filtering: bool = True


@dataclass
class TraumaContext:
    """Trauma-related context for healing rooms"""
    ace_score: float = 0.0
    trauma_types: List[str] = field(default_factory=list)
    trigger_words: List[str] = field(default_factory=list)
    safety_preferences: Dict[str, Any] = field(default_factory=dict)
    healing_goals: List[str] = field(default_factory=list)
    last_assessment: Optional[datetime] = None


@dataclass
class AIKnowledgeContext:
    """AI knowledge context for educational features"""
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    completed_modules: List[str] = field(default_factory=list)
    current_interests: List[str] = field(default_factory=list)
    preferred_style: Literal["visual", "textual", "interactive"] = "textual"
    ethics_understanding: float = 50.0
    last_quiz_score: Optional[float] = None


@dataclass
class UserContext:
    """Complete user context"""
    user_id: str
    session_id: str
    is_authenticated: bool
    user_profile: Optional[UserProfile] = None
    permissions: List[str] = field(default_factory=list)
    preferences: UserPreferences = field(default_factory=UserPreferences)
    trauma_context: Optional[TraumaContext] = None
    ai_knowledge_context: Optional[AIKnowledgeContext] = None


@dataclass
class RequestContext:
    """Request-specific context"""
    session_id: Optional[str] = None
    conversation_history: List[Message] = field(default_factory=list)
    user_preferences: Optional[UserPreferences] = None
    application_state: Optional[Dict[str, Any]] = None
    retrieved_docs: Optional[List[Dict[str, Any]]] = None
    brain_context: Optional[Dict[str, Any]] = None


@dataclass
class RequestMetadata:
    """Request metadata"""
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    referrer: Optional[str] = None
    device_type: Optional[Literal["desktop", "mobile", "tablet"]] = None
    language: Optional[str] = None


@dataclass
class BrainRequest:
    """Brain request structure"""
    id: str
    application: ApplicationType
    message: str
    user_context: UserContext
    context: Optional[RequestContext] = None
    metadata: Optional[RequestMetadata] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ResponseMetadata:
    """Response metadata"""
    provider: str
    model: str
    tokens_used: Optional[int] = None
    processing_time: float = 0.0
    confidence: Optional[float] = None
    sources: List[str] = field(default_factory=list)


@dataclass
class BrainResponse:
    """Brain response structure"""
    id: Optional[str] = None
    success: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[ResponseMetadata] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class HealthStatus:
    """Provider health status"""
    overall: Literal["healthy", "degraded", "unhealthy"]
    providers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    system: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BrainAnalytics:
    """Brain analytics data"""
    total_requests: int = 0
    success_rate: float = 0.0
    average_response_time: float = 0.0
    provider_usage: Dict[str, int] = field(default_factory=dict)
    application_usage: Dict[str, int] = field(default_factory=dict)
    user_satisfaction: float = 0.0
    error_rate: float = 0.0
    uptime: float = 0.0
    
    # Plugin system analytics
    active_plugins: int = 0
    plugin_usage: Dict[str, int] = field(default_factory=dict)
    workflow_executions: Dict[str, int] = field(default_factory=dict)
    data_source_usage: Dict[str, int] = field(default_factory=dict)
    
    # RAG analytics
    rag_usage: Dict[str, Any] = field(default_factory=lambda: {
        "queries": 0,
        "successful_retrievals": 0,
        "average_documents_retrieved": 0.0,
        "cache_hit_rate": 0.0
    })

