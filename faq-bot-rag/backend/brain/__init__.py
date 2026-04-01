"""
ThinkLife Brain - Generalized AI Orchestration System

This module contains the centralized AI Brain that manages all AI operations
across the ThinkLife platform using a plugin-based architecture.

Features:
- Plugin-based agent system with automatic discovery
- LangGraph workflow engine for standardized execution
- MCP integration for data source abstraction
- Trauma-informed safety systems
- Zero-code agent integration
"""

# Import main brain system
from .cortex import CortexFlow
from .specs import (
    BrainRequest, BrainResponse, BrainConfig,
    AgentExecutionSpec, DataSourceSpec, ProviderSpec, ToolSpec, ProcessingSpec,
    DataSourceType, ModelInfo, ProviderInfo,
    IAgent, IAgentPlugin, IConversationalAgent, ISafetyAwareAgent, IStreamingAgent,
    IDataSource, AgentMetadata, AgentConfig, AgentResponse, AgentCapability
)
from .cortex import ReasoningEngine, get_reasoning_engine, WorkflowEngine, get_workflow_engine, WorkflowStep, WorkflowStatus, WorkflowExecution
from .specs import ExecutionPlan
from .data_sources import (
    DataSourceRegistry, get_data_source_registry
)
from .guardrails import SecurityManager
from .tools import (
    get_tool_registry, ToolRegistry, BaseTool, ToolResult,
    create_tool, get_available_tools as get_available_tool_types
)
# Import tools conditionally (they may not all be available)
try:
    from .tools import TavilySearchTool
except ImportError:
    TavilySearchTool = None
try:
    from .tools import DocumentSummarizerTool
except ImportError:
    DocumentSummarizerTool = None

# Import providers
from . import providers

__version__ = "2.0.0"
    
__all__ = [
    # Main Cortex class
    "CortexFlow",
    
    # Core types
    "BrainRequest", 
    "BrainResponse",
    "BrainConfig",
    
    # Execution specifications
    "AgentExecutionSpec",
    "DataSourceSpec",
    "ProviderSpec",
    "ToolSpec",
    "ProcessingSpec",
    "DataSourceType",
    
    # Provider information
    "ModelInfo",
    "ProviderInfo",
    
    # Plugin system & Interfaces
    "IAgent",
    "IAgentPlugin", 
    "IConversationalAgent",
    "ISafetyAwareAgent",
    "IStreamingAgent",
    "IDataSource",
    "AgentMetadata",
    "AgentConfig",
    "AgentResponse",
    "AgentCapability",
    
    # Core Engines
    "ReasoningEngine",
    "WorkflowEngine",
    "WorkflowExecution",
    "WorkflowStep",
    "WorkflowStatus",
    "ExecutionPlan",
    "DataSourceRegistry",
    "SecurityManager",
    
    # Tools
    "ToolRegistry",
    "BaseTool",
    "ToolResult",
    "create_tool",
    "get_available_tool_types",
    
    # Providers
    "providers",
    
    # Utility functions
    "get_reasoning_engine",
    "get_workflow_engine",
    "get_data_source_registry",
    "get_tool_registry"
] 