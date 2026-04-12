"""
Shared types and data models for the evaluator framework.

This module defines the standard schemas for evaluation inputs and outputs
used across all evaluators (both common and FAQ-specific).
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class EvaluatorType(Enum):
    """Type of evaluator implementation."""
    LLM_BASED = "llm_based"  # Uses LLM-as-judge
    RULE_BASED = "rule_based"  # Uses deterministic rules


class BotType(Enum):
    """Supported bot types."""
    ZOE = "zoe"
    FAQ = "faq"


@dataclass
class EvaluationInput:
    """
    Standard input for all evaluators.

    Evaluators can use whichever fields are relevant to their evaluation logic.
    """
    # Required fields
    question: str  # User's query/question
    bot_response: str  # Bot's response to evaluate

    # Optional fields (used by specific evaluators)
    retrieved_docs: Optional[List[Dict[str, Any]]] = None  # For RAG evaluators
    expected_answer: Optional[str] = None  # For ground-truth comparisons
    conversation_history: Optional[List[Dict[str, str]]] = None  # For context-aware evaluation
    user_context: Optional[Dict[str, Any]] = None  # User metadata (ACE score, etc.)
    metadata: Optional[Dict[str, Any]] = None  # Additional bot metadata

    # Bot-specific fields
    bot_type: BotType = BotType.ZOE
    session_id: Optional[str] = None


@dataclass
class EvaluationResult:
    """
    Standard output from all evaluators.

    This consistent schema makes it easy to aggregate, display, and analyze results.
    """
    evaluator_name: str  # Name of the evaluator
    score: float  # Normalized score (0.0 to 1.0)
    passed: bool  # Whether the evaluation passed threshold
    label: Optional[str] = None  # Category label (e.g., "safe", "harmful", "excellent")
    explanation: str = ""  # Human-readable rationale
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional evaluator-specific data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "evaluator_name": self.evaluator_name,
            "score": self.score,
            "passed": self.passed,
            "label": self.label,
            "explanation": self.explanation,
            "metadata": self.metadata
        }


@dataclass
class TestCase:
    """
    A single test case for evaluation.

    Used in test_cases.json to define evaluation scenarios.
    """
    id: str
    question: str
    expected_answer: Optional[str] = None
    bot_type: str = "zoe"  # "zoe" or "faq"

    # Optional fields
    user_context: Optional[Dict[str, Any]] = None
    retrieved_docs: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_evaluation_input(self, bot_response: str) -> EvaluationInput:
        """Convert test case to evaluation input."""
        return EvaluationInput(
            question=self.question,
            bot_response=bot_response,
            retrieved_docs=self.retrieved_docs,
            expected_answer=self.expected_answer,
            user_context=self.user_context,
            metadata=self.metadata,
            bot_type=BotType(self.bot_type)
        )


@dataclass
class EvaluationSummary:
    """
    Aggregated summary of evaluation results.
    """
    total_cases: int
    total_evaluators: int
    overall_pass_rate: float
    results_by_evaluator: Dict[str, Dict[str, Any]]  # evaluator_name -> stats
    results_by_case: List[Dict[str, Any]]  # test_case_id -> all evaluator results

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_cases": self.total_cases,
            "total_evaluators": self.total_evaluators,
            "overall_pass_rate": self.overall_pass_rate,
            "results_by_evaluator": self.results_by_evaluator,
            "results_by_case": self.results_by_case
        }
