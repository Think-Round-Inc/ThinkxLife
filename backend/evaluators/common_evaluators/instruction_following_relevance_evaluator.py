"""
Instruction Following and Relevance Evaluator

Type: LLM-BASED

Evaluates whether the bot response:
1. Addresses the user's question appropriately
2. Stays relevant to the query
3. Follows implicit instructions (e.g., "give me 3 examples")
4. Provides useful information aligned with user intent

For Zoe bot: Checks that responses address emotional needs without going off-topic.
Evaluates appropriate redirects for out-of-scope requests.

For FAQ bot: Will verify responses directly answer the documentation question.
"""

from evaluators.base import LLMJudgeEvaluator
from evaluators.types import EvaluationInput


class InstructionFollowingRelevanceEvaluator(LLMJudgeEvaluator):
    """
    LLM-based evaluator for instruction following and relevance.
    """

    def __init__(self, pass_threshold: float = 0.7):
        """
        Initialize instruction following evaluator.

        Args:
            pass_threshold: Minimum score to pass (default 0.7)
        """
        super().__init__(pass_threshold=pass_threshold)

    def build_judge_prompt(self, evaluation_input: EvaluationInput) -> str:
        """
        Build the LLM judge prompt for relevance evaluation.

        Args:
            evaluation_input: Input containing question and bot response

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a relevance evaluator for chatbot responses. Evaluate whether the bot response appropriately addresses the user's question.

USER QUESTION:
{evaluation_input.question}

BOT RESPONSE:
{evaluation_input.bot_response}

Evaluate the response on the following criteria:

1. **Direct Relevance**: Does the response address the core question or concern?
   - Is the main topic of the response aligned with the question?
   - Does it provide relevant information or support?

2. **Instruction Following**: If the question contains implicit or explicit instructions, does the response follow them?
   - Examples: "give me 3 tips", "explain briefly", "help me with X"
   - Does the format and content match expectations?

3. **Usefulness**: Does the response provide value to the user?
   - Is it actionable or informative?
   - Does it move the conversation forward constructively?

4. **Appropriate Scope**:
   - If the question is out-of-scope, does the response politely redirect?
   - Does it avoid going off on tangents?
   - Does it maintain focus on the user's stated needs?

5. **Completeness**: Does the response adequately address the question?
   - Not too brief (dismissive)
   - Not too verbose (losing focus)
   - Covers key aspects of the question

Provide your evaluation as JSON:
{{
    "score": <float between 0.0 and 1.0, where 1.0 is perfectly relevant and helpful>,
    "label": "<highly_relevant|somewhat_relevant|off_topic>",
    "explanation": "<brief explanation of relevance and instruction following>"
}}

Score Guidelines:
- 1.0: Perfectly addresses question, follows all instructions
- 0.8-0.9: Highly relevant, minor omissions
- 0.6-0.7: Somewhat relevant but misses key points or instructions
- 0.4-0.5: Tangentially related, doesn't fully address question
- 0.0-0.3: Off-topic or irrelevant
"""
        return prompt
