"""
FAQ Exactness Evaluator

Type: LLM-BASED

Evaluates whether the FAQ bot's answer semantically matches the expected (ground-truth)
answer. This is used when a reference answer is available in the test case.

This is a semantic match evaluator — it checks whether the bot's response conveys
the same information as the expected answer, not whether it is word-for-word identical.
Paraphrasing and restructured-but-equivalent answers are acceptable.

Requires: expected_answer in EvaluationInput.
If no expected_answer is provided, the evaluator gracefully returns a neutral result.

TODO (FAQ bot integration):
- Build a ground truth dataset with expected_answer per FAQ question.
- Add expected_answer to test_cases.json entries that have known correct answers.
- Use this evaluator to track regression as FAQ bot changes over time.
"""

from evaluators.base import LLMJudgeEvaluator
from evaluators.types import EvaluationInput, EvaluationResult


class FAQExactnessEvaluator(LLMJudgeEvaluator):
    """
    LLM-based evaluator for semantic answer exactness against a reference answer.

    Gracefully skips evaluation when no expected_answer is provided.
    """

    def __init__(self, pass_threshold: float = 0.7):
        """
        Initialize FAQ exactness evaluator.

        Args:
            pass_threshold: Minimum semantic match score to pass (default 0.7)
        """
        super().__init__(pass_threshold=pass_threshold)

    def evaluate(self, evaluation_input: EvaluationInput) -> EvaluationResult:
        """
        Evaluate semantic answer exactness.

        Skips gracefully if no expected_answer is available.

        Args:
            evaluation_input: Must include expected_answer for meaningful evaluation

        Returns:
            EvaluationResult (neutral if no expected_answer)
        """
        if not evaluation_input.expected_answer:
            return self._create_result(
                score=0.5,
                explanation="No expected answer provided — exactness evaluation skipped. "
                            "Add expected_answer to this test case for ground-truth comparison.",
                label="skipped",
                metadata={"skipped": True, "reason": "no_expected_answer"}
            )

        return super().evaluate(evaluation_input)

    def build_judge_prompt(self, evaluation_input: EvaluationInput) -> str:
        """
        Build the LLM judge prompt for exactness evaluation.

        Args:
            evaluation_input: Input with bot_response and expected_answer

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an answer exactness evaluator for a documentation FAQ bot. Compare the bot's answer to the expected reference answer.

USER QUESTION:
{evaluation_input.question}

EXPECTED ANSWER (ground truth):
{evaluation_input.expected_answer}

BOT ANSWER:
{evaluation_input.bot_response}

Evaluate whether the bot's answer conveys the same core information as the expected answer:

1. **Key Information Coverage**: Does the bot's answer include all essential facts from the expected answer?
   - Main conclusion or directive matches
   - Key details, steps, or values are preserved

2. **Semantic Accuracy**: Is the meaning preserved even when different words are used?
   - Paraphrasing is acceptable
   - Restructured but equivalent information is acceptable
   - Synonyms and alternate phrasings are fine

3. **No Contradictions**: Does the bot's answer contradict any part of the expected answer?
   - No opposite claims
   - No misrepresentation of facts or procedures

4. **Scope Appropriateness**:
   - Not significantly shorter (missing important information)
   - Not significantly off-topic (adding irrelevant information)
   - Completeness proportional to the expected answer

Provide your evaluation as JSON:
{{
    "score": <float between 0.0 and 1.0, where 1.0 is a perfect semantic match>,
    "label": "<exact_match|partial_match|mismatch>",
    "explanation": "<brief explanation of how well the bot answer matches the expected answer, noting any gaps or contradictions>"
}}

Score Guidelines:
- 1.0: Conveys all the same information as the expected answer
- 0.8-0.9: Very close match with minor wording differences or slight omissions
- 0.6-0.7: Covers main points but misses notable details
- 0.4-0.5: Partial match with significant information gaps
- 0.0-0.3: Mostly wrong, contradicts expected answer, or completely off-topic
"""
        return prompt
