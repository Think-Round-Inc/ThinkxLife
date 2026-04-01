# Zoe Agent - Refactored Structure

## Overview

Zoe is ThinkLife's trauma-informed empathetic AI companion. All LLM processing goes through the centralized CortexFlow architecture.

## Architecture

```
Frontend → ZoeService → ZoeAgent (plugin) → CortexFlow → WorkflowEngine → Provider
```

## File Structure

### Core Files

- **`zoe_core.py`** - Domain logic handler
  - Personality and prompt building
  - Conversation context preparation
  - Response post-processing
  - Safety checks

- **`zoe_service.py`** - Frontend interface
  - Receives requests from frontend/API
  - Coordinates ZoeCore and ZoeAgent plugin
  - Handles confidence-based response decisions
  - Returns formatted responses with confidence scores

- **`personality.py`** - Trauma-informed personality system
  - Empathetic communication patterns
  - Safety checks and redirects
  - Trauma-aware responses

- **`conversation_manager.py`** - Session and conversation management
  - Session creation and tracking
  - Conversation history
  - Session cleanup

### Utilities

- **`helpers.py`** - Utility functions
  - `create_user_context()` - Creates UserContext for BrainRequest

- **`utils/knowledge_index_builder.py`** - Knowledge base index builder
  - Builds ChromaDB index from knowledge files
  - Previously `build_index.py`

### Services

- **`tts_service.py`** - Text-to-speech service
  - Converts text to speech for audio responses

## Usage

```python
from agents.zoe import ZoeService

# Initialize service
service = ZoeService()
await service.initialize()

# Process message
response = await service.process_message(
    message="I'm feeling anxious",
    user_id="user_123",
    user_context={"ace_score": 5}
)
```

## Removed Files

- **`brain_interface.py`** - Deprecated, removed (functionality moved to plugin)

## Confidence-Based Response Handling

### Overview
Zoe receives confidence scores (0.0-1.0) from the Brain for every response and makes context-aware decisions based on these scores.

### How It Works

**Brain generates confidence score:**
- Validates response quality
- Retries if confidence < 0.75 (up to 5 attempts)
- Returns response with confidence score

**Zoe makes final decision:**
```python
if confidence >= 0.75:
    # High confidence: Display brain's response
    return response
else:
    # Low confidence: Use context-aware fallback
    return empathetic_fallback()
```

### Context-Aware Fallbacks

Zoe analyzes the user's message type and provides appropriate responses:

**Emotional Support:**
```
"I hear that you're going through something difficult right now. While I'm 
not entirely certain I can give you the best specific advice on this, I want 
you to know that your feelings are valid..."
```

**Informational Questions:**
```
"I'm not completely confident I have the right information to answer that 
question accurately. Rather than give you potentially incorrect information, 
I think it would be better if you could rephrase your question..."
```

**Complex Messages:**
```
"I want to make sure I understand you correctly before responding. Could you 
help me by sharing what's most important to you right now?"
```

### Benefits
- Honest communication: Never provides potentially incorrect information
- Context-aware: Responses match the type of user message
- Trauma-informed: Low confidence responses are empathetic and supportive
- Transparent: Original response and confidence stored in metadata

## Key Principles

1. **Separation of Concerns**: Domain logic (ZoeCore) separate from LLM processing (Plugin)
2. **Centralized Processing**: All LLM calls go through CortexFlow
3. **Confidence-Based Decisions**: Zoe makes final decisions based on brain's confidence scores
4. **Trauma-Informed**: All responses consider trauma and safety
5. **Clean Interfaces**: Simple, clear APIs for frontend integration

