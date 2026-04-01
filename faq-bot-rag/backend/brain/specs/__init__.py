"""
Specifications module - All type definitions, contracts, and interfaces
"""

# Core specs
from .core_specs import (
    ApplicationType, MessageRole, BrainConfig, Message,
    UserProfile, UserPreferences, TraumaContext, AIKnowledgeContext, UserContext,
    RequestContext, RequestMetadata, BrainRequest,
    ResponseMetadata, BrainResponse,
    HealthStatus, BrainAnalytics
)

# Provider specs
from .provider_specs import (
    ProviderType, ModelInfo, ProviderInfo,
    ProviderConfig, LocalProviderConfig, OpenAIProviderConfig, 
    AnthropicProviderConfig, GeminiProviderConfig,
    ProviderSpec
)

# Tool specs
from .tool_specs import ToolSpec

# Data source specs
from .data_source_specs import (
    DataSourceType, DataSourceSpec, DataSourceInfo, IDataSource
)

# Guardrails specs
from .guardrails_specs import SecurityConfig

# Workflow specs
from .workflow_specs import (
    WorkflowStatus, WorkflowType, WorkflowStep, ProcessingSpec, WorkflowExecution, ExecutionPlan
)

# Reasoning specs
from .reasoning_specs import ReasoningContext

# Agent specs
from .agent_specs import (
    AgentCapability, PluginStatus,
    AgentMetadata, AgentConfig, AgentResponse, PluginInfo,
    AgentExecutionSpec,
    IAgent, IConversationalAgent, ISafetyAwareAgent, IStreamingAgent, IAgentPlugin
)

__all__ = [
    # Core
    "ApplicationType", "MessageRole", "BrainConfig", "Message",
    "UserProfile", "UserPreferences", "TraumaContext", "AIKnowledgeContext", "UserContext",
    "RequestContext", "RequestMetadata", "BrainRequest",
    "ResponseMetadata", "BrainResponse",
    "HealthStatus", "BrainAnalytics",
    
    # Provider
    "ProviderType", "ModelInfo", "ProviderInfo",
    "ProviderConfig", "LocalProviderConfig", "OpenAIProviderConfig",
    "AnthropicProviderConfig", "GeminiProviderConfig",
    "ProviderSpec",
    
    # Tool
    "ToolSpec",
    
    # Data Source
    "DataSourceType", "DataSourceSpec", "DataSourceInfo", "IDataSource",
    
    # Guardrails
    "SecurityConfig",
    
    # Workflow
    "WorkflowStatus", "WorkflowType", "WorkflowStep", "ProcessingSpec", "WorkflowExecution", "ExecutionPlan",
    
    # Reasoning
    "ReasoningContext",
    
    # Agent
    "AgentCapability", "PluginStatus",
    "AgentMetadata", "AgentConfig", "AgentResponse", "PluginInfo",
    "AgentExecutionSpec",
    "IAgent", "IConversationalAgent", "ISafetyAwareAgent", "IStreamingAgent", "IAgentPlugin",
]

