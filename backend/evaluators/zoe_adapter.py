"""
Zoe Bot Adapter

Provides a clean interface for the evaluator runner to obtain live responses
from the Zoe bot. The runner calls this adapter when a test case does not
include a pre-baked bot_response and the --live flag is passed.

This adapter initializes ZoeService (which in turn loads ZoeAgent, CortexFlow,
ChromaDB, and the configured LLM provider). All runtime dependencies must be
available for this to work.

Usage in the runner:
    from evaluators.zoe_adapter import ZoeBotAdapter
    import asyncio

    adapter = ZoeBotAdapter()
    response = asyncio.run(adapter.get_response("I'm feeling anxious"))

Requirements for --live mode:
- OPENAI_API_KEY must be set in the environment
- ChromaDB vector store must be available (or Zoe falls back gracefully)
- All backend dependencies in requirements.txt must be installed

TODO (FAQ bot integration):
- Create FAQBotAdapter following the same interface.
- Add get_response(question, retrieved_docs=None) method that calls FAQ bot logic.
- Register FAQBotAdapter in runner.py under the "faq" bot type.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ZoeBotAdapter:
    """
    Adapter that calls ZoeService to get live bot responses for evaluation.

    Interface contract:
        get_response(question, user_context=None) -> str

    The returned string is the bot's response text, ready to be placed in
    EvaluationInput.bot_response.
    """

    def __init__(self):
        self._service = None

    async def _ensure_initialized(self) -> bool:
        """Lazily initialize ZoeService on first use."""
        if self._service is not None:
            return True
        try:
            from agents.zoe.zoe_service import ZoeService
            self._service = ZoeService()
            initialized = await self._service.initialize()
            if not initialized:
                logger.error("ZoeService.initialize() returned False")
                return False
            return True
        except Exception as exc:
            logger.error(f"Failed to initialize ZoeService: {exc}")
            return False

    async def get_response(
        self,
        question: str,
        user_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Get a live response from the Zoe bot for a given question.

        Args:
            question: User question / message
            user_context: Optional dict with user metadata (e.g. ace_score)
            session_id: Optional session identifier for conversation continuity

        Returns:
            Bot response string, or an error message if Zoe is unavailable
        """
        ok = await self._ensure_initialized()
        if not ok:
            return (
                "[ZoeAdapter ERROR] Could not initialize ZoeService. "
                "Check that all backend dependencies are installed and "
                "OPENAI_API_KEY is set. Run without --live to use pre-baked responses."
            )

        try:
            result = await self._service.process_message(
                message=question,
                user_context=user_context or {},
                session_id=session_id,
            )
            return result.get("response", "[ZoeAdapter ERROR] Empty response from ZoeService")
        except Exception as exc:
            logger.error(f"ZoeService.process_message failed: {exc}")
            return f"[ZoeAdapter ERROR] {exc}"


class FAQBotAdapter:
    """
    Placeholder adapter for the FAQ bot.

    TODO (FAQ bot integration):
    Replace this stub with a real implementation that calls the FAQ bot's
    response generation pipeline. The interface must remain the same:

        get_response(question, user_context=None) -> str

    The returned string should be the FAQ bot's answer text.

    Typical integration steps:
    1. Import and initialize the FAQ bot service (e.g., FAQService).
    2. Call the FAQ bot's retrieval + generation pipeline.
    3. Return the response text.
    4. Optionally return retrieved_docs so the evaluator runner can
       pass them to FAQ-specific evaluators (update runner.py accordingly).
    """

    async def get_response(
        self,
        question: str,
        user_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Stub: returns a placeholder response until FAQ bot is implemented.

        Replace this method body with real FAQ bot call.
        """
        logger.warning(
            "FAQBotAdapter.get_response() called but FAQ bot is not yet implemented. "
            "Returning placeholder. Add bot_response to test_cases.json for offline evaluation."
        )
        return (
            "[FAQ Bot placeholder] The FAQ bot is not yet implemented. "
            "Add a bot_response field to your test case for offline evaluation, "
            "or implement FAQBotAdapter.get_response() once the FAQ bot is ready."
        )
