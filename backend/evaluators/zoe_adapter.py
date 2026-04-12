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
    Adapter that calls Sruthi's faq-bot-rag answer_question() for live evaluation.

    Returns (answer, retrieved_docs) so the runner can pass docs to FAQ-specific
    evaluators like AnswerFaithfulnessEvaluator and RetrievalPrecisionRecallEvaluator.

    Requires:
    - OPENAI_API_KEY set in environment
    - faq-bot-rag/data/vector_db/ must exist (run: python -m app.build_vector_db
      from the faq-bot-rag/ directory)
    """

    async def get_response(
        self,
        question: str,
        user_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> tuple:
        """
        Call answer_question() from faq-bot-rag and return (answer, retrieved_docs).

        retrieved_docs will be a list of dicts with keys: text, title, url, chunk_id.
        Returns (error_string, []) if the FAQ bot cannot be loaded.
        """
        import sys
        import os

        # Add project root to sys.path so faq-bot-rag is importable
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        try:
            from faq_bot_rag.app.rag_chat import answer_question
        except ImportError:
            # faq-bot-rag uses a hyphen in the directory name which Python can't import directly.
            # Fall back to importlib to load it by file path.
            import importlib.util
            rag_chat_path = os.path.join(project_root, "faq-bot-rag", "app", "rag_chat.py")
            spec = importlib.util.spec_from_file_location("rag_chat", rag_chat_path)
            rag_chat = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(rag_chat)
            except Exception as exc:
                logger.error(f"Failed to load rag_chat: {exc}")
                return (
                    "[FAQAdapter ERROR] Could not load faq-bot-rag. "
                    "Ensure the vector DB is built (python -m app.build_vector_db) "
                    "and OPENAI_API_KEY is set.",
                    []
                )
            answer_question = rag_chat.answer_question

        try:
            answer, docs, _ = answer_question(question)
            return answer, docs
        except Exception as exc:
            logger.error(f"answer_question() failed: {exc}")
            return f"[FAQAdapter ERROR] {exc}", []
