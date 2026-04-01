# Creating New Agents for ThinkLife Brain

## Quick Start

To create a new AI agent that integrates with the Brain system:

1. **Create your agent** in the `agents/` folder
2. **Create a plugin connector** in the `backend/plugins/` folder
3. **The Brain will automatically discover and load your agent**

## Agent Structure

```
agents/
├── your_agent/
│   ├── __init__.py           # Export your agent class
│   ├── your_agent_core.py    # Main agent implementation
│   ├── your_agent_config.py  # Configuration (optional)
│   └── other_files.py        # Additional functionality
└── plugins/
    └── your_agent_plugin.py  # Plugin connector (lightweight!)
```

## Step 1: Create Your Agent

Create your agent folder and implement the core logic:

```python
# agents/your_agent/__init__.py
from .your_agent_core import YourAgentCore

__all__ = ["YourAgentCore"]
```

```python
# agents/your_agent/your_agent_core.py
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class YourAgentCore:
    """
    Your agent's main implementation
    Handle your domain logic, state management, and business rules here
    """
    
    def __init__(self):
        self.agent_type = "your_agent"
        self.capabilities = ["conversational", "analytical"]  # Define your capabilities
        
    async def process_message(self, message: str, user_context: Dict[str, Any]) -> str:
        """
        Process a user message and return a response
        This is where your agent's intelligence lives
        """
        # Your agent logic here
        return f"Response to: {message}"
    
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        # Return conversation history
        return []
    
    async def update_context(self, session_id: str, context: Dict[str, Any]) -> bool:
        """Update conversation context"""
        # Update your agent's context
        return True
    
    async def assess_safety(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess message safety"""
        # Your safety logic
        return {"safe": True, "confidence": 1.0}
```

## Step 2: Create Plugin Connector

Create a lightweight plugin in `backend/plugins/` that connects your agent to the Brain:

```python
# backend/plugins/your_agent_plugin.py
import logging
import time
from typing import Dict, Any, List, Optional

from brain.types import (
    IAgent, IAgentPlugin, IConversationalAgent, ISafetyAwareAgent,
    AgentMetadata, AgentConfig, AgentResponse, BrainRequest,
    AgentCapability
)
from agents.your_agent import YourAgentCore  # Import your agent

logger = logging.getLogger(__name__)

class YourAgent(IConversationalAgent, ISafetyAwareAgent):
    """
    Lightweight connector between Brain and YourAgent
    All domain logic stays in YourAgentCore - this just bridges the connection
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_id = config.agent_id
        self._initialized = False
        self.agent_core: Optional[YourAgentCore] = None

    @property
    def metadata(self) -> AgentMetadata:
        """Return your agent's metadata"""
        return AgentMetadata(
            name="Your Agent Name",
            version="1.0.0",
            description="Description of what your agent does",
            capabilities=[
                AgentCapability.CONVERSATIONAL,
                AgentCapability.ANALYTICAL,  # Add your capabilities
            ],
            supported_applications=[
                "chatbot",        # Applications your agent handles
                "general",        # Add more as needed
            ],
            author="Your Name"
        )

    async def initialize(self, config: AgentConfig) -> bool:
        """Initialize your agent"""
        if self._initialized:
            return True
            
        try:
            # Initialize your agent core
            self.agent_core = YourAgentCore()
            self._initialized = True
            logger.info(f"YourAgent {self.agent_id} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing YourAgent: {str(e)}")
            return False

    async def process_request(self, request: BrainRequest) -> AgentResponse:
        """Process request by delegating to your agent core"""
        if not self._initialized or not self.agent_core:
            return AgentResponse(
                success=False,
                content="Agent not available right now. Please try again later.",
                metadata={"error": "Agent not initialized"}
            )
        
        start_time = time.time()
        
        try:
            # Convert Brain request to your agent's format
            message = request.message
            user_context = request.user_context.__dict__ if request.user_context else {}
            
            # Call your agent's core logic
            response_content = await self.agent_core.process_message(message, user_context)
            
            return AgentResponse(
                success=True,
                content=response_content,
                metadata={
                    "agent_type": "your_agent",
                    "session_id": request.context.session_id if request.context else None
                },
                processing_time=time.time() - start_time,
                session_id=request.context.session_id if request.context else None
            )
            
        except Exception as e:
            logger.error(f"Error processing request in YourAgent: {str(e)}")
            return AgentResponse(
                success=False,
                content="I encountered an error processing your request.",
                metadata={"error": str(e)},
                processing_time=time.time() - start_time
            )

    async def can_handle_request(self, request: BrainRequest) -> float:
        """Return confidence score for handling this request"""
        # Implement logic to determine if your agent can handle this request
        # Return 0.0 (cannot handle) to 1.0 (perfect match)
        
        # Example: handle general requests with high confidence
        if request.application == "general":
            return 0.9
        elif request.application == "chatbot":
            return 0.8
        return 0.0  # Cannot handle other applications

    # IConversationalAgent methods
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history via your agent core"""
        if self.agent_core:
            return await self.agent_core.get_conversation_history(session_id)
        return []

    async def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation via your agent core"""
        # Implement if your agent supports this
        return True

    async def update_context(self, session_id: str, context: Dict[str, Any]) -> bool:
        """Update context via your agent core"""
        if self.agent_core:
            return await self.agent_core.update_context(session_id, context)
        return False

    # ISafetyAwareAgent methods
    async def assess_content_safety(self, request: BrainRequest) -> Dict[str, Any]:
        """Assess content safety via your agent core"""
        if self.agent_core:
            user_context = request.user_context.__dict__ if request.user_context else {}
            return await self.agent_core.assess_safety(request.message, user_context)
        return {"safe": True, "confidence": 1.0}

    async def apply_content_filters(self, response: AgentResponse) -> AgentResponse:
        """Apply content filters to response"""
        # Add any content filtering logic here
        return response

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            "status": "healthy" if self._initialized else "unhealthy",
            "agent_id": self.agent_id,
            "initialized": self._initialized,
            "agent_type": "your_agent"
        }

    async def shutdown(self) -> None:
        """Shutdown agent"""
        self.agent_core = None
        self._initialized = False
        logger.info(f"YourAgent {self.agent_id} shutdown complete")


class YourAgentPlugin(IAgentPlugin):
    """Plugin factory for YourAgent"""

    def create_agent(self, config: AgentConfig) -> IAgent:
        """Factory method to create YourAgent instance"""
        return YourAgent(config)

    def get_metadata(self) -> AgentMetadata:
        """Get plugin metadata"""
        return AgentMetadata(
            name="Your Agent Name",
            version="1.0.0", 
            description="Description of what your agent does",
            capabilities=[
                AgentCapability.CONVERSATIONAL,
                AgentCapability.ANALYTICAL,
            ],
            supported_applications=[
                "chatbot",
                "general",
            ],
            author="Your Name"
        )

    def validate_config(self, config: AgentConfig) -> bool:
        """Validate agent configuration"""
        return True  # Add validation logic if needed


# Export the plugin for auto-discovery
__all__ = ["YourAgent", "YourAgentPlugin"]
```

## Key Concepts

### Agent vs Plugin Separation
- **Agent** (`agents/your_agent/`): Contains your business logic, domain expertise, and state management
- **Plugin** (`backend/plugins/your_agent_plugin.py`): Lightweight connector that bridges your agent to the Brain system

### Required Interfaces

1. **IAgent** - Core agent contract:
   - `process_request()` - Main processing logic
   - `can_handle_request()` - Routing confidence (0.0-1.0)

2. **IConversationalAgent** - Chat capabilities:
   - `get_conversation_history()`
   - `update_context()`

3. **ISafetyAwareAgent** - Safety features:
   - `assess_content_safety()`
   - `apply_content_filters()`

### Configuration
Your agent can receive configuration through the `AgentConfig`:
```python
# In your plugin's initialize method
self.max_history = config.config.get("max_history", 20)
self.response_style = config.config.get("response_style", "friendly")
```

## Agent Discovery

The Brain automatically discovers your agent by:
1. Scanning the `agents/` folder
2. Looking for `*_plugin.py` files in `backend/plugins/`
3. Importing and registering the plugin class

## Testing Your Agent

```python
# Test your agent directly
from agents.your_agent import YourAgentCore
from brain.brain_core import GeneralizedBrain

async def test_agent():
    # Initialize Brain
    brain = GeneralizedBrain()
    await brain.initialize()
    
    # Test request
    request = {
        "id": "test",
        "message": "Hello, test agent!",
        "application": "general",
        "user_context": {"user_id": "test_user"}
    }
    
    response = await brain.process_request(request)
    print(f"Response: {response}")
```

## Agent Capabilities

Choose and implement the capabilities that match your agent:

```python
AgentCapability.CONVERSATIONAL    # Chat and dialogue
AgentCapability.CREATIVE         # Creative content generation  
AgentCapability.ANALYTICAL       # Data analysis and reasoning
AgentCapability.EDUCATIONAL      # Teaching and learning
AgentCapability.SEARCH          # Information retrieval
AgentCapability.MULTIMODAL      # Text, images, audio, etc.
AgentCapability.TOOL_USE        # Using external tools
AgentCapability.DATA_PROCESSING # Handling structured data
```

## Best Practices

1. **Keep plugins lightweight** - All heavy logic should be in your agent's core
2. **Handle errors gracefully** - Always return proper `AgentResponse` objects
3. **Use proper logging** - Include meaningful log messages for debugging
4. **Test thoroughly** - Test both your agent core and plugin integration
5. **Document capabilities** - Clearly define what your agent can and cannot do

## Next Steps

1. **Create your agent folder** and implement the core logic
2. **Create the plugin connector** in `backend/plugins/`
3. **Test your integration** using the Brain system
4. **Add more capabilities** as needed (safety, conversation management, etc.)

Your agent will be automatically discovered and ready to handle requests!
