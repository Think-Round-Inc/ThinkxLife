"""
ThinkLife Evaluator Framework

Offline evaluation framework for the Zoe and FAQ bots.
All evaluators share a common input/output contract defined in types.py.

Quick start:
    # From backend/ directory:
    python -m evaluators.runner --bot zoe --input evaluators/test_cases.json

Evaluator types:
    - LLM-BASED: Uses an OpenAI judge prompt for subjective quality dimensions.
    - RULE-BASED: Uses deterministic code (no LLM call needed).

Structure:
    evaluators/
      base.py                     # BaseEvaluator, LLMJudgeEvaluator
      types.py                    # EvaluationInput, EvaluationResult, BotType, TestCase
      runner.py                   # CLI runner
      zoe_adapter.py              # Adapter for calling Zoe (and FAQ bot placeholder)
      test_cases.json             # Sample test cases for smoke testing
      common_evaluators/          # Shared across Zoe and FAQ bot
      faq_evaluators/             # FAQ bot only (some are stubs until FAQ bot is built)
"""

from evaluators.types import (
    EvaluationInput,
    EvaluationResult,
    EvaluatorType,
    BotType,
    TestCase,
    EvaluationSummary,
)
from evaluators.base import BaseEvaluator, LLMJudgeEvaluator

__all__ = [
    "EvaluationInput",
    "EvaluationResult",
    "EvaluatorType",
    "BotType",
    "TestCase",
    "EvaluationSummary",
    "BaseEvaluator",
    "LLMJudgeEvaluator",
]
