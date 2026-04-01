"""
Agent specifications, interfaces, and types
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentCapability(str, Enum):
    """Agent capabilities"""
    CONVERSATIONAL = "conversational"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    SEARCH = "search"
    TOOL_USE = "tool_use"


class PluginStatus(str, Enum):
    """Plugin status types"""
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class AgentMetadata:
    """Metadata describing an agent's capabilities"""
    name: str
    version: str
    description: str
    capabilities: List[AgentCapability]
    supported_applications: List[str]
    requires_auth: bool = True
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentConfig:
    """Configuration for agent initialization"""
    agent_id: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Standardized agent response"""
    success: bool
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: Optional[float] = None
    processing_time: float = 0.0
    session_id: Optional[str] = None


@dataclass
class PluginInfo:
    """Information about a registered plugin"""
    plugin_id: str
    name: str
    version: str
    description: str
    status: PluginStatus
    capabilities: List[str] = field(default_factory=list)
    supported_applications: List[str] = field(default_factory=list)
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    error_count: int = 0


@dataclass
class AgentExecutionSpec:
    """
    Complete specification from agent to Brain about how to process the request
    
    This is what agents pass to Brain to specify:
    - Which data sources to use
    - Which provider and configuration
    - Which tools to apply
    - How to process the request
    """
    data_sources: List[Any] = field(default_factory=list)  # List[DataSourceSpec]
    provider: Optional[Any] = None  # Optional[ProviderSpec]
    tools: List[Any] = field(default_factory=list)  # List[ToolSpec]
    processing: Any = None  # ProcessingSpec
    
    # Optional agent-specific metadata
    agent_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "data_sources": [ds.to_dict() if hasattr(ds, 'to_dict') else ds for ds in self.data_sources],
            "provider": self.provider.to_dict() if hasattr(self.provider, 'to_dict') else self.provider,
            "tools": [tool.to_dict() if hasattr(tool, 'to_dict') else tool for tool in self.tools],
            "processing": self.processing.to_dict() if hasattr(self.processing, 'to_dict') else self.processing,
            "agent_metadata": self.agent_metadata
        }


# Interfaces

class IAgent(ABC):
    """
    Base interface that all Brain agents must implement
    
    Agents specify execution requirements via create_execution_specs(),
    and Brain executes according to those specifications.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> AgentMetadata:
        """Return agent metadata"""
        pass
    
    @abstractmethod
    async def initialize(self, config: AgentConfig) -> bool:
        """Initialize the agent"""
        pass
    
    @abstractmethod
    async def create_execution_specs(self, request: Any) -> AgentExecutionSpec:  # request: BrainRequest
        """
        Agent specifies how Brain should process the request:
        - Which data sources to query
        - Which LLM provider and configuration to use
        - Which tools to apply
        - Processing requirements (iterations, timeout, etc.)
        
        Brain executes exactly what agent specifies.
        """
        pass
    
    @abstractmethod
    async def process_request(self, request: Any) -> AgentResponse:  # request: BrainRequest
        """
        Process a user request and return response
        
        Agents implement domain logic, Brain handles LLM execution via specifications.
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Clean shutdown of agent resources"""
        pass
    
    async def can_handle_request(self, request: Any) -> float:  # request: BrainRequest
        """
        Return confidence score (0.0-1.0) for handling this request
        Default implementation checks supported applications
        """
        application = request.application
        if application in self.metadata.supported_applications:
            return 0.8
        return 0.0


class IConversationalAgent(IAgent):
    """
    Interface for agents that maintain conversation context
    Agents implementing this manage their own conversation history
    """
    
    @abstractmethod
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        pass
    
    @abstractmethod
    async def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history"""
        pass
    
    @abstractmethod
    async def update_context(self, session_id: str, context: Dict[str, Any]) -> bool:
        """Update conversation context"""
        pass


class ISafetyAwareAgent(IAgent):
    """
    Interface for agents with safety and content filtering
    """
    
    @abstractmethod
    async def assess_content_safety(self, request: Any) -> Dict[str, Any]:  # request: BrainRequest
        """
        Assess request for safety concerns
        
        Returns:
            Dict with keys: safe (bool), concerns (list), severity (str)
        """
        pass
    
    @abstractmethod
    async def apply_content_filters(self, response: AgentResponse) -> AgentResponse:
        """Apply content filters to response"""
        pass


class IStreamingAgent(IAgent):
    """Interface for agents that support streaming responses"""
    
    @abstractmethod
    async def stream_response(self, request: Any) -> AsyncGenerator[str, None]:  # request: BrainRequest
        """Stream response chunks as they're generated"""
        pass


class IAgentPlugin(ABC):
    """
    Interface for agent plugins that can be dynamically loaded
    Plugins create agent instances and provide metadata
    """
    
    @abstractmethod
    def create_agent(self, config: AgentConfig) -> IAgent:
        """Factory method to create agent instance"""
        pass
    
    @abstractmethod
    def get_metadata(self) -> AgentMetadata:
        """Get plugin metadata"""
        pass
    
    @abstractmethod
    def validate_config(self, config: AgentConfig) -> bool:
        """Validate configuration before agent creation"""
        pass

