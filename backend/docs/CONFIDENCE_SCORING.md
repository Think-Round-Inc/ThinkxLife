# Confidence Scoring System

## Overview

The ThinkLife Brain implements an intelligent **Confidence Scoring System** that automatically evaluates the quality and reliability of every AI-generated response. Each response receives a confidence score between **0.0 (no confidence) and 1.0 (complete confidence)**, allowing the system to make informed decisions about whether to accept, retry, or replace responses.

## Why Confidence Scoring?

Traditional AI systems either return responses blindly or use binary pass/fail validation. Our confidence scoring system provides:

- **Quantified uncertainty**: Know exactly how confident the AI is in each response
- **Automatic quality control**: Poor responses are caught and improved before reaching users
- **Honest communication**: When confidence is low, users receive transparent "I don't know" responses instead of potentially incorrect information
- **Reduced hallucinations**: Low confidence responses are filtered out
- **Better user experience**: Users receive either high-quality answers or honest acknowledgment of limitations

## How It Works

### Three-Stage Pipeline

```
Response Generated
       ↓
[1. Rule-Based Checks] → Quick validation (30% weight)
       ↓
[2. LLM Evaluation] → Deep quality assessment (70% weight)
       ↓
[3. Weighted Combination] → Final confidence score (0.0-1.0)
       ↓
Confidence >= 0.75? → YES: Accept | NO: Retry or Fallback
```

## Detailed Scoring Process

### Stage 1: Rule-Based Checks (30% weight)

Fast, deterministic checks that catch obvious issues:

| Check | Pass Criteria | Fail Score | Pass Score |
|-------|---------------|------------|------------|
| **Length** | >= 10 characters | 0.1 | Continue |
| **Word Count** | >= 3 words | 0.2 | Continue |
| **Error Patterns** | No refusal phrases | 0.3 | Continue |
| **All Checks Pass** | - | - | 0.5 |

**Error Patterns Detected:**
- "i cannot", "i can't", "i don't have"
- "i'm unable", "as an ai"
- "i apologize, but", "i'm sorry, but"

**Example:**
```python
# Response: "I can't help with that."
# → Detected error pattern + short response
# → Confidence: 0.3
```

### Stage 2: LLM-Based Evaluation (70% weight)

The system asks an LLM to evaluate the response across four dimensions:

| Dimension | Points | Evaluates |
|-----------|--------|-----------|
| **Relevance** | 0-25 | Is the response on-topic and addressing the question? |
| **Helpfulness** | 0-25 | Does it provide useful, actionable information? |
| **Accuracy** | 0-25 | Is the information correct and free from errors? |
| **Completeness** | 0-25 | Is the response fully formed and comprehensive? |
| **Total** | **0-100** | Overall quality score |

**LLM Validation Prompt:**
```
Evaluate this AI response and provide a confidence score.

User Message: {user_message}
AI Response: {response}

Evaluate:
1. Relevance to the user's question (0-25 points)
2. Helpfulness and informativeness (0-25 points)
3. Accuracy and correctness (0-25 points)
4. Completeness (not cut off, addresses the question) (0-25 points)

Respond in this EXACT format:
SCORE: <number 0-100>
REASONING: <brief explanation>
```

**Example LLM Response:**
```
SCORE: 85
REASONING: The response is highly relevant and provides helpful information. 
It's mostly accurate but could be more complete in addressing edge cases.
```

### Stage 3: Weighted Combination

The final confidence score combines both evaluations:

```python
final_confidence = (rule_based_score × 0.3) + (llm_score × 0.7)
```

**Why this weighting?**
- **30% Rule-Based**: Fast pre-screening, catches obvious failures
- **70% LLM-Based**: Deep semantic understanding, evaluates actual quality

## Calculation Examples

### Example 1: High Quality Response

**User Question:** "What are some coping strategies for anxiety?"

**AI Response:** "Here are evidence-based coping strategies for anxiety: 1) Deep breathing exercises, 2) Progressive muscle relaxation, 3) Mindfulness meditation, 4) Regular physical exercise, and 5) Cognitive restructuring. Each of these techniques has been shown to reduce anxiety symptoms effectively."

**Calculation:**
```python
# Stage 1: Rule-based
Pass: Length: 200+ chars
Pass: Word count: 30+ words
Pass: No error patterns
rule_based_score = 0.5

# Stage 2: LLM evaluation
Relevance: 25/25 (directly answers the question)
Helpfulness: 24/25 (provides actionable strategies)
Accuracy: 24/25 (evidence-based information)
Completeness: 23/25 (comprehensive list)
Total: 96/100
llm_score = 0.96

# Stage 3: Final score
final_confidence = (0.5 × 0.3) + (0.96 × 0.7)
                 = 0.15 + 0.672
                 = 0.822

Result: 0.822 >= 0.75 → ACCEPTED
```

### Example 2: Poor Quality Response

**User Question:** "What are some coping strategies for anxiety?"

**AI Response:** "I can't provide medical advice."

**Calculation:**
```python
# Stage 1: Rule-based
Pass: Length: 30 chars
Pass: Word count: 5 words
Fail: Error pattern detected: "I can't"
rule_based_score = 0.3  # Fails due to refusal pattern

# Stage 2: LLM evaluation
Relevance: 5/25 (acknowledges topic but doesn't answer)
Helpfulness: 3/25 (not helpful)
Accuracy: 15/25 (technically correct but unhelpful)
Completeness: 5/25 (incomplete response)
Total: 28/100
llm_score = 0.28

# Stage 3: Final score
final_confidence = (0.3 × 0.3) + (0.28 × 0.7)
                 = 0.09 + 0.196
                 = 0.286

Result: 0.286 < 0.75 → REJECTED → RETRY
```

### Example 3: Borderline Response

**User Question:** "How does quantum computing work?"

**AI Response:** "Quantum computing uses quantum bits or qubits that can exist in multiple states simultaneously through superposition. This allows quantum computers to process information differently than classical computers."

**Calculation:**
```python
# Stage 1: Rule-based
Pass: All checks pass
rule_based_score = 0.5

# Stage 2: LLM evaluation
Relevance: 23/25 (on topic)
Helpfulness: 18/25 (basic explanation, lacks detail)
Accuracy: 22/25 (correct but simplified)
Completeness: 18/25 (missing key concepts)
Total: 81/100
llm_score = 0.81

# Stage 3: Final score
final_confidence = (0.5 × 0.3) + (0.81 × 0.7)
                 = 0.15 + 0.567
                 = 0.717

Result: 0.717 < 0.75 → REJECTED → RETRY
```

## Threshold & Decision Logic

### The 0.75 Threshold

We use **0.75 as the acceptance threshold** based on:

- **High quality bar**: Ensures only well-formed, helpful responses pass
- **Balanced strictness**: Not too lenient (risk of poor responses) or too strict (too many retries)
- **Empirical testing**: 0.75 provides optimal balance between quality and retry rate

### Decision Flow

The brain stops retrying when either condition is met:
- Confidence reaches 0.75 or higher (success)
- Completes 5 validation attempts (max limit)

```python
if confidence >= 0.75:
    # ACCEPT: Stop immediately, return response
    return response_to_agent()
else:
    if validation_attempts < max_validation_runs (5):
        # RETRY: Loop back with feedback
        retry_with_feedback()
    else:
        # MAX ATTEMPTS: Stop retrying, replace with fallback
        replace_with_fallback()
        # Agent still receives response with low confidence score
        return response_to_agent()
```

### Two-Layer Response Handling

**Brain Level (Workflow Engine):**
- Generates and validates responses
- Retries up to 5 times if confidence < 0.75
- After max attempts: Replaces with generic fallback
- Always returns response with confidence score

**Agent Level (e.g., Zoe):**
- Receives response with confidence score
- Makes final decision based on confidence
- If confidence >= 0.75: Displays response
- If confidence < 0.75: Uses context-aware fallback

This separation allows:
- Brain focuses on quality control and retries
- Agents make context-aware decisions for their domain
- Different agents can handle low confidence differently

## Configuration

### Default Settings

```python
# workflow_engine.py - WorkflowState initialization
{
    "confidence_score": 0.0,
    "validation_attempts": 0,
    "max_validation_runs": 5,  # Maximum retry attempts
    "is_validated": False
}

# Threshold
CONFIDENCE_THRESHOLD = 0.75  # Hardcoded in validation logic

# Weighting
RULE_BASED_WEIGHT = 0.3
LLM_BASED_WEIGHT = 0.7

# LLM Validation Settings
VALIDATION_TEMPERATURE = 0.3  # Low temperature for consistent scoring
VALIDATION_MAX_TOKENS = 200
```

### Customization Options

**Change the threshold:**
```python
# workflow_engine.py, line ~645
is_valid = final_confidence >= 0.75  # Change to 0.70 or 0.80
```

**Change max retry attempts:**
```python
# workflow_engine.py, line ~145
"max_validation_runs": 5,  # Change to 3 or 7
```

**Change weighting:**
```python
# workflow_engine.py, line ~637
final_confidence = (confidence_score * 0.3) + (llm_confidence * 0.7)
# Example: More weight to rules: (confidence_score * 0.4) + (llm_confidence * 0.6)
```

## API Response Format

### Brain/Workflow Response

```json
{
    "success": true,
    "content": "The AI response text...",
    "confidence": 0.822,
    "execution_id": "abc-123-def",
    "status": "completed",
    "metadata": {
        "confidence_score": 0.822,
        "validation_attempts": 1,
        "execution_steps": ["initialize", "build_messages", "call_provider", "validate_response", "finalize"],
        "errors": [],
        "duration_seconds": 2.45
    }
}
```

### Zoe Service Response (Agent Level)

```json
{
    "success": true,
    "response": "Here are some coping strategies...",
    "confidence": 0.822,
    "session_id": "session-456",
    "metadata": {
        "low_confidence": false,
        "processing_time": 2.5,
        "agent": "zoe"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Low Confidence Response (Zoe Fallback)

```json
{
    "success": true,
    "response": "I'm not completely confident I have the right information to answer that question accurately...",
    "confidence": 0.68,
    "session_id": "session-456",
    "metadata": {
        "low_confidence": true,
        "original_confidence": 0.68,
        "original_response": "The stored but not displayed response...",
        "processing_time": 3.2,
        "agent": "zoe"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Agent-Level Handling (Zoe Example)

### How Zoe Uses Confidence Scores

Zoe receives the confidence score from the brain and makes context-aware decisions:

```python
# zoe_service.py
confidence = agent_response.metadata.get("confidence_score", 0.0)

if confidence < 0.75:
    # Use context-aware fallback
    zoe_fallback = self._get_low_confidence_response(message, confidence)
    return zoe_fallback  # Empathetic "I don't know" style response
else:
    # Display the high-confidence response
    return agent_response.content
```

### Context-Aware Fallbacks

Zoe analyzes the user's message and provides appropriate fallback responses:

**For emotional support requests:**
```
"I hear that you're going through something difficult right now. While I'm 
not entirely certain I can give you the best specific advice on this, I want 
you to know that your feelings are valid..."
```

**For informational questions:**
```
"I'm not completely confident I have the right information to answer that 
question accurately. Rather than give you potentially incorrect information, 
I think it would be better if you could rephrase your question..."
```

**For complex/unclear messages:**
```
"I want to make sure I understand you correctly before responding. Could you 
help me by sharing what's most important to you right now?"
```

## Retry Mechanism

### How Retries Improve Confidence

When confidence < 0.75, the system:

1. **Captures validation feedback** from the LLM evaluation
2. **Injects feedback into system prompt** for the next attempt
3. **Regenerates response** with guidance to improve
4. **Re-evaluates** with fresh confidence calculation

**Retry Prompt Enhancement:**
```
IMPORTANT - Response Improvement Required:
Your previous response was not satisfactory.

Previous response: {truncated_response}

Feedback: Confidence too low (0.68): The response lacks depth and doesn't 
fully address the user's question about coping strategies.

Please generate a better, more helpful, and complete response that addresses 
the user's question properly.
```

### Retry Success Example

```
Attempt 1: "Try breathing exercises." 
    Confidence: 0.52 
    Action: RETRY

Attempt 2: "Breathing exercises can help. Try inhaling for 4 counts..." 
    Confidence: 0.71 
    Action: RETRY

Attempt 3: "Here are evidence-based coping strategies: 1) Deep breathing: Inhale for 4 counts, hold for 4, exhale for 4..." 
    Confidence: 0.83 
    Action: ACCEPTED
```

### Complete Flow Example: Max Attempts with Low Confidence

User asks: "What is the best treatment for PTSD?"

**Brain Workflow:**
```
Attempt 1: "Try meditation" → Confidence: 0.52 → RETRY
Attempt 2: "Therapy helps" → Confidence: 0.61 → RETRY
Attempt 3: "CBT and EMDR..." → Confidence: 0.69 → RETRY
Attempt 4: "Professional help..." → Confidence: 0.71 → RETRY
Attempt 5: "Various treatments..." → Confidence: 0.73 → MAX ATTEMPTS REACHED

Brain Finalize Node:
- Check: 0.73 < 0.75
- Action: Replace with fallback message
- New content: "I'm not confident I can provide an accurate answer to that question right now."

Brain returns to Zoe:
{
    "content": "I'm not confident I can provide an accurate answer...",
    "confidence": 0.73,
    "validation_attempts": 5
}
```

**Zoe Service:**
```python
confidence = 0.73  # Received from brain

if confidence < 0.75:
    # Analyze message context: "PTSD treatment" is medical/emotional
    # Use Zoe's empathetic fallback instead of brain's generic one
    response = "I hear that you're looking for guidance on PTSD treatment. 
                While I want to help, this is an important medical question 
                that I'm not fully confident I can answer accurately. I strongly 
                recommend speaking with a mental health professional who can 
                provide proper diagnosis and treatment options."

User receives: Zoe's context-aware empathetic fallback
```

## Benefits & Use Cases

### Benefits

1. **Quality Assurance**: Only high-quality responses (≥0.75) reach users
2. **Transparent Uncertainty**: System acknowledges when it doesn't know
3. **Reduced Hallucinations**: Low confidence = honest fallback instead of guessing
4. **Self-Improving**: Retries with feedback progressively improve responses
5. **Measurable**: Quantified confidence enables monitoring and analytics
6. **Agent Independence**: Different agents can use confidence differently

### Use Cases

**Healthcare/Therapy (Zoe):**
- High confidence: Provide coping strategies
- Low confidence: Acknowledge limitations, suggest professional help

**Customer Support:**
- High confidence: Answer directly
- Low confidence: Escalate to human agent

**Educational Assistants:**
- High confidence: Teach the concept
- Low confidence: Recommend authoritative resources

**General Chatbots:**
- High confidence: Direct answer
- Low confidence: Ask clarifying questions

## Monitoring & Analytics

### Key Metrics to Track

1. **Average confidence score** across all responses
2. **Confidence distribution** (histogram)
3. **Retry rate** (% of responses requiring retries)
4. **Acceptance rate after retry** (how often retries succeed)
5. **Fallback rate** (% reaching max attempts with low confidence)
6. **Confidence by message type** (emotional vs informational)

### Log Examples

```
INFO: Response validated successfully (attempt 1, confidence: 0.85)
WARNING: Response validation failed (attempt 2, confidence: 0.65): Confidence too low
INFO: Workflow abc-123 finished: completed (confidence: 0.78, attempts: 2)
INFO: Low confidence response (0.68), using Zoe's fallback
```

## Implementation Files

- **`backend/brain/cortex/workflow_engine.py`**: Core confidence calculation logic
- **`backend/agents/zoe/zoe_service.py`**: Agent-level confidence handling
- **`backend/brain/cortex/cortex.py`**: Reasoning validation
- **`backend/VALIDATION_LOOP_IMPLEMENTATION.md`**: Full system documentation

## Best Practices

### For Developers

1. **Always check confidence** in response handling
2. **Log confidence scores** for monitoring
3. **Customize thresholds** based on use case criticality
4. **Use confidence metadata** for debugging
5. **Test edge cases** (exactly 0.75, very low, very high)

### For System Administrators

1. **Monitor confidence trends** over time
2. **Adjust threshold** if too many retries or fallbacks
3. **Review low confidence cases** for system improvement
4. **Track retry success rates** to optimize feedback prompts
5. **A/B test** different threshold values

### For Agents/Applications

1. **Design appropriate fallbacks** for low confidence
2. **Consider context** when handling low confidence
3. **Store confidence** in conversation history
4. **Provide transparency** to users when appropriate
5. **Use confidence** for routing decisions (human vs AI)

## Troubleshooting

### Problem: Too many retries

**Symptom:** Most responses require 3+ attempts

**Solutions:**
- Lower threshold to 0.70
- Adjust LLM weight (increase rule-based to 0.4)
- Review and improve base prompts
- Check if LLM validator is too strict

### Problem: Poor responses passing

**Symptom:** Low quality responses getting ≥0.75 confidence

**Solutions:**
- Increase threshold to 0.80
- Improve rule-based checks (add more patterns)
- Increase LLM weight to 0.8
- Review LLM validation prompt for clarity

### Problem: High latency

**Symptom:** Slow response times due to validation

**Solutions:**
- Reduce validation max_tokens to 150
- Use faster provider for validation
- Cache validation results for similar responses
- Skip LLM validation for very short responses

## Future Enhancements

1. **Adaptive thresholds** based on message type
2. **Confidence calibration** using historical data
3. **Multi-model validation** (ensemble confidence)
4. **User feedback loop** to improve scoring
5. **Confidence explanation** returned to frontend
6. **A/B testing framework** for threshold optimization

---

## Quick Reference

### Key Numbers
- **Threshold**: 0.75
- **Max Retries**: 5
- **Rule Weight**: 30%
- **LLM Weight**: 70%
- **Validation Temp**: 0.3

### Confidence Ranges
- **0.0-0.3**: Very low (obvious failures)
- **0.3-0.5**: Low (rule violations or poor content)
- **0.5-0.75**: Moderate (needs improvement)
- **0.75-0.9**: Good (acceptable quality)
- **0.9-1.0**: Excellent (high quality)

### Decision Logic
```
confidence >= 0.75  →  Accept
confidence < 0.75 AND attempts < 5  →  Retry
confidence < 0.75 AND attempts >= 5  →  Fallback
```

---

