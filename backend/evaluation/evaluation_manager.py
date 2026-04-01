"""
ThinkLife Evaluation System with LangFuse Observability

Evaluation framework for AI responses with:
- Response latency monitoring
- LangFuse integration for tracing and monitoring (v3.x)

Usage:
    from evaluation.evaluation_manager import evaluate_response, get_evaluation_manager
    
    # Run evaluation
    results = await evaluate_response(
        user_message="I'm feeling anxious",
        bot_message="I hear that you're feeling anxious...",
        start_time=start_timestamp,
        end_time=end_timestamp,
        context={"user_id": "user_123", "session_id": "session_456"}
    )
    
    # Access latency evaluator
    manager = get_evaluation_manager()
    latency_result = await manager.latency_evaluator.evaluate(start_time, end_time)
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .evaluators.latency_evaluator import LatencyEvaluator

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# --- Langfuse Client Implementation ---

# Conditional import for Langfuse
try:
    from langfuse import Langfuse, observe
    LANGFUSE_AVAILABLE = True
    logger.info("Langfuse package imported successfully (v3.7.0+)")
except ImportError as e:
    logger.warning(f"Langfuse not available: {e}. Install with: pip install langfuse>=3.7.0")
    LANGFUSE_AVAILABLE = False
    Langfuse = None
    # Create no-op decorator
    def observe(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator

# Global singleton client
_langfuse_client: Optional[Langfuse] = None
_langfuse_initialized: bool = False


def initialize_langfuse_client() -> bool:
    """
    Initialize Langfuse client singleton for tracing (Langfuse 3.7.0+)
    """
    global _langfuse_client, _langfuse_initialized
    
    if _langfuse_initialized:
        return _langfuse_client is not None
    
    _langfuse_initialized = True
    
    if not LANGFUSE_AVAILABLE:
        return False
    
    try:
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")
        
        if not public_key or not secret_key:
            logger.warning("Langfuse credentials not found.")
            return False
        
        _langfuse_client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
        
        if _langfuse_client.auth_check():
            logger.info(f"Langfuse client authenticated (host: {host})")
            return True
        else:
            logger.error("Langfuse authentication failed")
            _langfuse_client = None
            return False
            
    except Exception as e:
        logger.error(f"Langfuse client initialization failed: {e}")
        _langfuse_client = None
        return False


def get_langfuse_client() -> Optional[Langfuse]:
    return _langfuse_client


def is_langfuse_enabled() -> bool:
    return _langfuse_client is not None


def flush_langfuse():
    global _langfuse_client
    if _langfuse_client is not None:
        try:
            _langfuse_client.flush()
        except Exception as e:
            logger.error(f"Error flushing Langfuse events: {e}")


def reset_langfuse_client():
    global _langfuse_client, _langfuse_initialized
    if _langfuse_client is not None:
        try:
            _langfuse_client.flush()
        except Exception:
            pass
    _langfuse_client = None
    _langfuse_initialized = False

# --- End Langfuse Client Implementation ---


class EvaluationManager:
    """
    Manages and coordinates evaluators with LangFuse observability
    Replaces the old EvaluationRegistry
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.latency_evaluator = LatencyEvaluator()
        logger.info("Evaluation Manager initialized")

    @observe(name="run_full_evaluation")
    async def evaluate_response(
        self,
        user_message: str,
        bot_message: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}
        
        try:
            # Run latency evaluation
            latency_result = None
            if start_time is not None and end_time is not None:
                latency_result = await self.latency_evaluator.evaluate(start_time, end_time, context)
            
            results = {}
            if latency_result:
                results["latency"] = latency_result
            
            # Calculate aggregate scores
            aggregate_scores = self._calculate_aggregate_scores(results)
            results["aggregate_scores"] = aggregate_scores
            
            results["evaluation_metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "evaluators_run": 1 if latency_result else 0,
                "context": context
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {"error": str(e), "success": False}

    def _calculate_aggregate_scores(self, results: Dict[str, Any]) -> Dict[str, Any]:
        score_breakdown = {}
        if "latency" in results and isinstance(results["latency"], dict):
            if "performance_score" in results["latency"]:
                score_breakdown["performance_score"] = results["latency"]["performance_score"]
        
        overall_score = score_breakdown.get("performance_score", 0.0)
        
        return {
            "overall_quality_score": round(overall_score, 3),
            "score_breakdown": score_breakdown,
            "quality_level": self._get_quality_level(overall_score)
        }

    def _get_quality_level(self, score: float) -> str:
        if score >= 0.9: return "excellent"
        elif score >= 0.75: return "good"
        elif score >= 0.6: return "acceptable"
        else: return "needs_improvement"

    def get_latency_statistics(self) -> Dict[str, Any]:
        return self.latency_evaluator.get_summary_statistics()

    def reset_latency_statistics(self):
        self.latency_evaluator.reset_statistics()


# Global state
_evaluation_manager: Optional[EvaluationManager] = None

def initialize_evaluation_manager(llm_client=None) -> EvaluationManager:
    global _evaluation_manager
    if _evaluation_manager is None:
        _evaluation_manager = EvaluationManager(llm_client=llm_client)
    return _evaluation_manager

def get_evaluation_manager() -> EvaluationManager:
    global _evaluation_manager
    if _evaluation_manager is None:
        _evaluation_manager = EvaluationManager()
    return _evaluation_manager

# Convenience wrapper
async def evaluate_response(
    user_message: str,
    bot_message: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    context: Optional[Dict[str, Any]] = None,
    llm_client=None,
    enable_tracing: bool = False
) -> Dict[str, Any]:
    if enable_tracing and not is_langfuse_enabled():
        initialize_langfuse_client()
    
    manager = get_evaluation_manager()
    if llm_client:
        manager.llm_client = llm_client
        
    return await manager.evaluate_response(
        user_message, bot_message, start_time, end_time, context
    )

def get_latency_statistics() -> Dict[str, Any]:
    return get_evaluation_manager().get_latency_statistics()

def reset_latency_statistics():
    get_evaluation_manager().reset_latency_statistics()

# Export main functions
__all__ = [
    "evaluate_response",
    "get_evaluation_manager",
    "initialize_evaluation_manager",
    "get_latency_statistics",
    "reset_latency_statistics",
    "initialize_langfuse_client",
    "get_langfuse_client",
    "is_langfuse_enabled",
    "flush_langfuse",
    "reset_langfuse_client",
    "LANGFUSE_AVAILABLE"
]
