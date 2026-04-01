# Zoe Plugin Architecture - Ultra Lightweight

## Simplified Plugin Design

The Zoe plugin is **ultra-lightweight** - it only contains LLM request specifications and invokes cortex for processing.

## Plugin Structure

```python
class ZoeAgent:
    """
    Lightweight plugin containing:
    - LLM specs (provider, model, params)
    - Data source specs
    - Tool specs
    - Processing specs
    
    Invokes cortex for all processing
    """
    
    # LLM Request Specifications
    llm_specs = {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.8,
        "max_tokens": 1500,
        "params": {
            "top_p": 0.9,
            "presence_penalty": 0.3,
            "frequency_penalty": 0.2
        }
    }
    
    # Data source specifications
    data_sources = [
        {
            "type": "conversation_history",
            "enabled": True,
            "limit": 10
        },
        {
            "type": "vector_db",
            "enabled": True,
            "limit": 3,
            "filters": {"trauma_informed": True}
        }
    ]
    
    # Tool specifications
    tools = []
    
    # Processing specifications
    processing = {
        "execution_strategy": "adaptive",
        "reasoning_threshold": 0.75,
        "max_iterations": 2,
        "timeout_seconds": 30.0
    }
```

## Request Flow (Simplified)

```
User Request
    ↓
┌─────────────────────────────────────┐
│  ZOE PLUGIN                          │
│  (Ultra Lightweight)                 │
│                                      │
│  Contains:                           │
│  • llm_specs = {...}                 │
│  • data_sources = [...]              │
│  • tools = [...]                     │
│  • processing = {...}                │
│                                      │
│  Does:                               │
│  1. create_execution_specs()         │
│  2. cortex.process_agent_request()   │
│  3. Return response                  │
└─────────┬───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│  CORTEX                              │
│  (Handles Everything)                │
│                                      │
│  • Load ZoeCore from agents/zoe/     │
│  • Process request with specs        │
│  • Handle LLM calls                  │
│  • Manage conversation               │
│  • Return response                   │
└─────────────────────────────────────┘
```

## Complete Plugin Code

```python
"""
Zoe Agent Plugin - Lightweight connector

Contains LLM request specs and invokes cortex
"""

class ZoeAgent(IConversationalAgent):
    def __init__(self, config: AgentConfig):
        self.agent_id = config.agent_id
        self._initialized = False
        
        # LLM specifications
        self.llm_specs = {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.8,
            "max_tokens": 1500,
            "params": {
                "top_p": 0.9,
                "presence_penalty": 0.3,
                "frequency_penalty": 0.2
            }
        }
        
        # Data sources
        self.data_sources = [...]
        
        # Tools
        self.tools = []
        
        # Processing
        self.processing = {...}
    
    async def create_execution_specs(self, request: BrainRequest):
        """Return stored specs as dict"""
        return {
            "llm": self.llm_specs,
            "data_sources": self.data_sources,
            "tools": self.tools,
            "processing": self.processing,
            "metadata": {...}
        }
    
    async def process_request(self, request: BrainRequest):
        """Invoke cortex with specs"""
        # Get specs
        specs = await self.create_execution_specs(request)
        
        # Invoke cortex
        cortex = CortexFlow()
        result = await cortex.process_agent_request(
            request=request,
            agent=self,
            execution_specs=specs
        )
        
        # Return response
        return AgentResponse(...)
```

## Key Points

### Plugin Responsibilities:
1. **Store** LLM request specs (provider, model, params)
2. **Store** data source specs
3. **Store** tool specs  
4. **Store** processing specs
5. **Invoke** cortex for processing
6. **Return** result

### Plugin Does NOT:
- Handle LLM calls
- Manage conversations
- Build prompts
- Process responses
- Connect to ZoeCore directly
- Orchestrate execution

### Cortex Handles:
- Load ZoeCore from `agents/zoe/`
- Process agent request
- Execute LLM calls
- Manage conversation
- Build prompts
- Post-process responses
- All orchestration

## Size Comparison

### Before (Complex):
- 400+ lines
- Orchestrated everything
- Connected to multiple systems
- Complex flow management

### After (Simple):
- ~150 lines
- Just specs + invoke
- Single cortex call
- Clean and minimal

## Benefits

1. **Ultra Simple** - Just specs and one cortex call
2. **Easy to Maintain** - Change specs, that's it
3. **Clear Separation** - Plugin = specs, Cortex = processing
4. **Flexible** - Easy to adjust LLM params
5. **Reusable** - Same pattern for all agents

## Adjusting LLM Specs

To change Zoe's LLM configuration:

```python
# In plugins/zoe_agent.py

# Change provider
self.llm_specs = {
    "provider": "anthropic",  # Changed
    "model": "claude-3-sonnet",  # Changed
    ...
}

# Adjust temperature
self.llm_specs["temperature"] = 0.9

# Add data source
self.data_sources.append({
    "type": "web_search",
    "enabled": True,
    "limit": 5
})

# Add tool
self.tools.append({
    "name": "search",
    "enabled": True
})
```

That's it! No other code changes needed.

## File Structure

```
backend/
├── plugins/
│   └── zoe_agent.py          ← ULTRA LIGHTWEIGHT
│       • Contains specs
│       • Invokes cortex
│       (~150 lines)
│
├── agents/
│   └── zoe/
│       ├── zoe_core.py       ← DOMAIN LOGIC
│       ├── personality.py    ← PERSONALITY
│       └── conversation_manager.py  ← CONVERSATIONS
│
└── brain/
    └── cortex/
        └── cortex.py         ← PROCESSES EVERYTHING
            • Loads ZoeCore
            • Handles LLM calls
            • Manages flow
```

## Summary

**Plugin = Specs Container + Cortex Invoker**

```python
# That's the entire plugin logic:
specs = plugin.get_specs()
result = cortex.process(request, specs)
return result
```

**Simple. Clean. Maintainable.**
