# Cortex & Reasoning Architecture

## Cortex (The Brain Core)

**Cortex** (`backend/brain/cortex/cortex.py`) is the orchestrator. It implements a **Two-Phase Execution Model**:

1.  **Phase 1: Planning** (Deciding *what* to do)
2.  **Phase 2: Execution** (Doing it)

### Responsibilities

*   **Singleton:** Initializes all subsystems (Reasoning, Workflow, Security).
*   **Guardrails:** Checks Auth, Rate Limiting, and Content Safety *before* planning.
*   **Estimation:** Predicts Cost and Latency using `CostEstimator` and `LatencyEstimator`.
*   **Planning:** Creates an `ExecutionPlan`.

### Planning Strategies

Cortex supports three strategies, defined in `AgentExecutionSpec`:

1.  **Direct (`_create_direct_plan`):**
    *   **Fastest.** Uses the agent's specs exactly as provided.
    *   No extra LLM calls.
    *   Used for simple chat or well-defined tasks.

2.  **Reasoned (`_create_reasoned_plan`):**
    *   **Smart.** Calls `ReasoningEngine` to optimize the specs.
    *   Can add/remove tools, change data sources, or refine the prompt.
    *   Adds latency but improves quality for complex tasks.

3.  **Adaptive (`_create_adaptive_plan`):**
    *   **Balanced.** Calls `ReasoningEngine` but only uses the optimized plan if confidence is high.
    *   Falls back to direct execution if reasoning is uncertain.

---

## Reasoning Engine

**Reasoning Engine** (`backend/brain/cortex/reasoning_engine.py`) is the "Pre-frontal Cortex". It uses an LLM to "think" about the request before acting.

### Capabilities

1.  **Optimize Specs:**
    *   Input: Original `AgentExecutionSpec`, User Request, Context.
    *   Output: `optimized_specs`, `confidence`, `notes`.
    *   *Example:* User asks "What's the weather?". Reasoning adds `weather_tool` if not present.

2.  **Tool Selection:**
    *   Dynamically picks the best tools from the registry based on the query.

3.  **Data Source Selection:**
    *   Decides if Vector DB is needed or if the query is purely conversational.

### Integration

The Reasoning Engine is called *only* during the Planning Phase. It does not execute the final call.

```python
# Cortex.py
plan = await self.reasoning_engine.optimize_execution_specs(...)
```

### Reasoning Validation

Before workflow execution, Cortex validates the reasoning engine output to ensure quality:

**Validation Checks:**
1. Plan exists with valid specs
2. Provider is specified (type and model)
3. Reasoning confidence >= 0.3 (minimum threshold)
4. Optimized specs differ from original (if reasoning was applied)
5. Cost and latency estimates are non-negative

**Validation Behavior:**
- If valid: Proceeds to workflow execution
- If invalid: Returns error response immediately, prevents execution
- Logs validation failures at ERROR level

**Example:**
```python
# cortex.py - After creating execution plan
validation = self._validate_reasoning_output(plan, request)
if not validation["valid"]:
    return error_response(validation["issues"])
```

### Observability

*   **Reasoning Steps:** All internal "thoughts" (LLM calls for reasoning) are traced in Langfuse.
*   **Confidence Scores:** Returned metrics help tune the system (e.g., "I'm 90% sure we need search").
*   **Validation Results:** Reasoning validation outcomes are logged for monitoring.

---

## Relationship Diagram

```
User Request
    ↓
[Cortex]
    ↓
(Check Guardrails)
    ↓
(Strategy Check) --[Direct]--> [ExecutionPlan]
        |                            ↓
    [Reasoned/Adaptive]         [Workflow Engine]
        ↓
    [Reasoning Engine] --(LLM Call to Plan)--> [Optimized Specs]
        ↓
    [ExecutionPlan]
        ↓
    [Validate Reasoning Output] --[Invalid]--> Error Response
        ↓ [Valid]
    [Workflow Engine]
        ↓
    [Validate Response + Confidence Scoring]
        ↓
    [Response to Agent]
```
