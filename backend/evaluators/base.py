"""
Base classes and interfaces for evaluators.

All evaluators should inherit from BaseEvaluator and implement the evaluate() method.
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
import os
from openai import OpenAI

from evaluators.types import EvaluationInput, EvaluationResult, EvaluatorType


class BaseEvaluator(ABC):
    """
    Base class for all evaluators.

    Subclasses must implement:
    - evaluate(): The main evaluation logic
    - evaluator_type: Class property indicating LLM_BASED or RULE_BASED
    """

    evaluator_type: EvaluatorType = EvaluatorType.RULE_BASED  # Override in subclass

    def __init__(self, pass_threshold: float = 0.7):
        """
        Initialize evaluator.

        Args:
            pass_threshold: Minimum score (0.0-1.0) for evaluation to pass
        """
        self.pass_threshold = pass_threshold
        self.name = self.__class__.__name__.replace("Evaluator", "").lower()

    @abstractmethod
    def evaluate(self, evaluation_input: EvaluationInput) -> EvaluationResult:
        """
        Evaluate the bot response.

        Args:
            evaluation_input: Standardized input containing question, response, and optional context

        Returns:
            EvaluationResult with score, pass/fail, and explanation
        """
        pass

    def _create_result(
        self,
        score: float,
        explanation: str,
        label: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> EvaluationResult:
        """
        Helper to create standardized evaluation result.

        Args:
            score: Normalized score (0.0 to 1.0)
            explanation: Human-readable rationale
            label: Optional category label
            metadata: Optional additional data

        Returns:
            EvaluationResult
        """
        return EvaluationResult(
            evaluator_name=self.name,
            score=score,
            passed=score >= self.pass_threshold,
            label=label,
            explanation=explanation,
            metadata=metadata or {}
        )


class LLMJudgeEvaluator(BaseEvaluator):
    """
    Base class for evaluators that use LLM-as-judge.

    Provides common functionality for calling LLM with structured prompts.
    """

    evaluator_type = EvaluatorType.LLM_BASED

    def __init__(self, pass_threshold: float = 0.7, model: str = "gpt-4o-mini"):
        """
        Initialize LLM-based evaluator.

        Args:
            pass_threshold: Minimum score for passing
            model: OpenAI model to use for judging
        """
        super().__init__(pass_threshold)
        self.model = model
        # Lazy: client is created on first LLM call so the evaluator can be
        # instantiated without OPENAI_API_KEY (e.g. for unit tests or rule-based
        # subclasses that override evaluate() before calling call_llm_judge).
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        """OpenAI client, initialized lazily on first access."""
        if self._client is None:
            self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return self._client

    @abstractmethod
    def build_judge_prompt(self, evaluation_input: EvaluationInput) -> str:
        """
        Build the prompt for the LLM judge.

        This should be implemented by each subclass to create evaluator-specific prompts.

        Args:
            evaluation_input: Input data for evaluation

        Returns:
            Formatted prompt string
        """
        pass

    def call_llm_judge(self, prompt: str) -> dict:
        """
        Call the LLM with the judge prompt and parse the response.

        Expected LLM response format (JSON):
        {
            "score": float (0.0-1.0),
            "label": str,
            "explanation": str
        }

        Args:
            prompt: The judge prompt

        Returns:
            Parsed JSON response from LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert evaluator. Respond with valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Deterministic for consistency
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            # Fallback in case of API error
            return {
                "score": 0.0,
                "label": "error",
                "explanation": f"LLM judge error: {str(e)}"
            }

    def evaluate(self, evaluation_input: EvaluationInput) -> EvaluationResult:
        """
        Evaluate using LLM-as-judge.

        Args:
            evaluation_input: Standardized input

        Returns:
            EvaluationResult
        """
        prompt = self.build_judge_prompt(evaluation_input)
        llm_response = self.call_llm_judge(prompt)

        return self._create_result(
            score=llm_response.get("score", 0.0),
            explanation=llm_response.get("explanation", ""),
            label=llm_response.get("label"),
            metadata={"llm_response": llm_response}
        )
