# ThinkLife Brain

The central AI orchestration system for the ThinkLife platform, featuring a plugin-based architecture and trauma-informed design.

## Overview

The ThinkLife Brain is a generalized AI system that manages all AI operations across the platform. It provides:

- Plugin-based agent system with automatic discovery
- Trauma-informed safety built into interactions
- LangGraph workflow engine for standardized execution
- MCP integration for data source abstraction
- Backward compatibility with existing integrations

## Structure

The system is organized into the following components:

- **brain/**: Core orchestration system
  - **cortex/**: Main orchestration logic (Cortex, Reasoning, Workflow)
  - **data_sources/**: Data abstraction layer
  - **guardrails/**: Security and session management
  - **providers/**: LLM provider implementations (OpenAI, Gemini, Anthropic)
  - **specs/**: Data structures and type definitions
  - **tools/**: Tool definitions and registry
- **agents/**: Domain-specific agent logic (e.g., Zoe)
- **evaluation/**: Estimators and evaluators for performance and quality
- **middleware/**: Authentication and request handling
- **plugins/**: Connector layer between agents and the Brain

## Quick Start

### Basic Usage

```python
from brain import CortexFlow

# Initialize with configuration
brain_config = {
    "providers": {
        "openai": {
            "enabled": True,
            "api_key": "your-api-key",
            "model": "gpt-4o-mini"
        }
    }
}

brain = CortexFlow(brain_config)

# Process requests
request = {
    "message": "Hello, I need support",
    "application": "healing-rooms",
    "user_context": {"user_id": "user123", "ace_score": 2}
}

response = await brain.process_request(request)
```

### Health Monitoring

```python
# Check system health
health = await brain.get_health_status()
print(f"System status: {health['overall']}")

# Get analytics
analytics = await brain.get_analytics()
print(f"Total requests: {analytics['total_requests']}")
```

## Plugin System

To create a new agent:

1. Create your agent logic in `agents/your_agent/` folder.
2. Create a plugin connector in `backend/plugins/your_agent_plugin.py`.
3. The Brain automatically discovers and loads the agent.

See `docs/CREATING_AGENTS.md` for detailed instructions.

## Configuration

### Provider Configuration

```python
{
    "providers": {
        "openai": {
            "enabled": True,
            "api_key": "your-key",
            "model": "gpt-4o-mini",
            "max_tokens": 2000,
            "temperature": 0.7
        }
    }
}
```

### Security Configuration

Security features are automatically enabled:
- Rate limiting: 60 requests per minute per user
- Content filtering: Trauma-safe mode enabled
- Input sanitization: XSS and injection protection

## Documentation

- **[System Architecture](docs/BRAIN_ARCHITECTURE.md)**: Complete system overview
- **[Creating Agents](docs/CREATING_AGENTS.md)**: Guide to build new agents
- **[Workflow Engine](docs/WORKFLOW_ENGINE.md)**: Details on the execution engine
- **[Cortex & Reasoning](docs/CORTEX_REASONING_ARCHITECTURE.md)**: Planning and reasoning logic

## Key Benefits

1. **Modular**: Add new agents without modifying core code.
2. **Trauma-Informed**: Safety features built into the core.
3. **Efficient**: Optimized routing and execution planning.
4. **Scalable**: Architecture supports growth and multiple agents.
5. **Maintainable**: Clear separation of concerns.
