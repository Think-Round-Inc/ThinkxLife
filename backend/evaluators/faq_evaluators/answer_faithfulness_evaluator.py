"""
Answer Faithfulness Evaluator

Type: LLM-BASED

Evaluates whether the FAQ bot's answer is faithful to the retrieved documentation.
This is critical for RAG systems to ensure answers don't hallucinate or contradict
the source material.

Key checks:
- Does the answer claim information not in the retrieved docs?
- Does the answer contradict the documentation?
- Are all claims grounded in the provided context?

This evaluator requires:
- bot_response: The FAQ bot's answer
- retrieved_docs: The documentation used to generate the answer

TODO (FAQ bot integration):
- Connect to FAQ bot response generation
- Ensure retrieved_docs are passed with document IDs for citation tracking
"""

from evaluators.base import LLMJudgeEvaluator
from evaluators.types import EvaluationInput


class AnswerFaithfulnessEvaluator(LLMJudgeEvaluator):
    """
    LLM-based evaluator for answer faithfulness to source documents.
    """

    def __init__(self, pass_threshold: float = 0.8):
        """
        Initialize faithfulness evaluator.

        Args:
            pass_threshold: Minimum faithfulness score to pass (default 0.8 - high bar)
        """
        super().__init__(pass_threshold=pass_threshold)

    def build_judge_prompt(self, evaluation_input: EvaluationInput) -> str:
        """
        Build the LLM judge prompt for faithfulness evaluation.

        Args:
            evaluation_input: Input with bot_response and retrieved_docs

        Returns:
            Formatted prompt string
        """
        if not evaluation_input.retrieved_docs:
            # Can't evaluate faithfulness without retrieved docs
            return self._build_no_context_prompt()

        # Format retrieved documents
        context_str = ""
        for i, doc in enumerate(evaluation_input.retrieved_docs, 1):
            content = doc.get("content", doc.get("text", ""))
            doc_id = doc.get("id", f"doc_{i}")
            context_str += f"\n[{doc_id}]: {content}\n"

        prompt = f"""You are a faithfulness evaluator for a documentation FAQ bot. Evaluate whether the bot's answer is faithful to the provided source documents.

USER QUESTION:
{evaluation_input.question}

SOURCE DOCUMENTATION:
{context_str}

BOT ANSWER:
{evaluation_input.bot_response}

Evaluate the answer on the following criteria:

1. **Grounding**: Are all factual claims in the answer supported by the source documents?
   - Check each statement against the documentation
   - Identify any claims not found in the sources

2. **No Hallucination**: Does the answer avoid adding information not in the sources?
   - Extra details or examples not from documentation
   - Assumptions or inferences beyond what's written
   - "Creative" elaborations

3. **No Contradiction**: Does the answer avoid contradicting the source material?
   - Check for opposite claims
   - Check for misrepresentation of procedures or policies

4. **Appropriate Extrapolation**: If the answer makes reasonable inferences:
   - Are they clearly marked as such?
   - Are they logical extensions of documented information?
   - Do they stay within the scope of the documentation?

5. **Completeness of Citation**: Does the answer reflect the key information from relevant docs?
   - Important details not omitted
   - Context preserved

Provide your evaluation as JSON:
{{
    "score": <float between 0.0 and 1.0, where 1.0 is perfectly faithful>,
    "label": "<faithful|mostly_faithful|unfaithful>",
    "explanation": "<brief explanation identifying any faithfulness issues, specific claims that are unsupported or contradictory>"
}}

Score Guidelines:
- 1.0: Perfectly faithful, all claims grounded in sources
- 0.8-0.9: Faithful with minor elaborations or reasonable inferences
- 0.6-0.7: Mostly faithful but includes some unsupported claims
- 0.4-0.5: Multiple unsupported claims or minor contradictions
- 0.0-0.3: Major hallucinations or contradicts documentation
"""
        return prompt

    def _build_no_context_prompt(self) -> str:
        """Fallback prompt when no retrieved docs available."""
        return """{{
    "score": 0.0,
    "label": "no_context",
    "explanation": "Cannot evaluate faithfulness - no source documents provided"
}}"""

    def evaluate(self, evaluation_input: EvaluationInput) -> "EvaluationResult":
        """
        Evaluate answer faithfulness.

        Args:
            evaluation_input: Must include retrieved_docs for meaningful evaluation

        Returns:
            EvaluationResult
        """
        if not evaluation_input.retrieved_docs:
            return self._create_result(
                score=0.0,
                explanation="Cannot evaluate faithfulness without retrieved documents",
                label="no_context",
                metadata={"error": "missing_retrieved_docs"}
            )

        return super().evaluate(evaluation_input)


# FAQ BOT INTEGRATION GUIDE:
#
# When FAQ bot is implemented, ensure the following:
#
# 1. Pass retrieved documents with the response:
#    evaluation_input = EvaluationInput(
#        question=user_query,
#        bot_response=faq_response,
#        retrieved_docs=retrieved_documents  # From RAG retrieval step
#    )
#
# 2. Include document IDs in retrieved_docs for citation tracking:
#    retrieved_docs = [
#        {"id": "doc_123", "content": "..."},
#        {"id": "doc_456", "content": "..."}
#    ]
#
# 3. Consider pre-filtering retrieved docs to only include high-relevance docs
#    to reduce noise in faithfulness evaluation
#
# 4. Use this evaluator during development to catch hallucination issues early
