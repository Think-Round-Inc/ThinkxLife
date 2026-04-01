# Langfuse Setup (Cloud)

ThinkLife uses **Langfuse** for observability, tracing, and evaluation of AI agent performance.

## Cloud Setup

1.  **Sign Up:** Go to [cloud.langfuse.com](https://cloud.langfuse.com) and sign up.
2.  **Create Project:** Create a new project (e.g., "ThinkLife Dev").
3.  **Get API Keys:** Go to **Settings** -> **API Keys**. Create new keys.

## Environment Variables

Add the following to your `backend/.env` file:

```bash
# Langfuse Tracing
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://us.cloud.langfuse.com
```

## Backend Integration

The Langfuse client is centrally managed in `backend/evaluation/evaluation_manager.py`.

### Automatic Tracing
We use the `@observe` decorator to trace key functions.

*   **Cortex:** `process_agent_request`
*   **Workflow Engine:** `execute_plan`, `_execute_graph`, `_call_provider_node`
*   **Zoe Agent:** Traces are propagated from the agent logic.

### Example Usage

In any file where you want to trace a function:

```python
try:
    from langfuse import observe
except ImportError:
    # Fallback no-op decorator
    def observe(*args, **kwargs):
        def decorator(f): return f
        return decorator

@observe(name="my_function")
def my_function(arg):
    # ... logic ...
    return result
```

## Features Enabled

1.  **Traces:** See full execution paths from Agent -> Cortex -> Workflow -> Provider.
2.  **Generations:** See exact prompts sent to LLMs and their responses.
3.  **Latency:** Track how long each step takes.
4.  **Cost:** Track token usage and estimated costs (if model pricing is known).
5.  **Scores:** (Optional) Attach quality scores to traces using Evaluators.

## Troubleshooting

*   **"Langfuse import failed":** Ensure `langfuse` package is installed (`pip install langfuse`).
*   **No traces appearing:** Check your keys in `.env`. Ensure `LANGFUSE_HOST` is set correctly.
*   **Performance impact:** Langfuse tracing is asynchronous and minimal impact, but ensure network connectivity is stable.
