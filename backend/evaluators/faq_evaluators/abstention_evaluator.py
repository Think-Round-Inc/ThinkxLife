"""
Abstention Evaluator

Type: LLM-BASED

Evaluates whether the FAQ bot appropriately abstains (i.e., says "I don't know"
or "I can't find this in the documentation") when a question cannot be answered
from available documentation — versus hallucinating an answer with false confidence.

Two failure modes this catches:
1. Under-abstention: Bot confidently answers when it has no supporting documentation.
2. Over-abstention: Bot refuses to answer when documentation clearly supports an answer.

Good abstention behavior:
- Honest acknowledgment of knowledge gaps
- Suggests alternative resources or escalation paths
- Does not fabricate plausible-sounding but unsupported answers

TODO (FAQ bot integration):
- Add test cases specifically designed to trigger abstention
  (e.g., questions outside the documented domain).
- Pair with retrieval_precision_recall_evaluator to see if abstention correlates
  with low retrieval quality.
- Define "out-of-scope" topics for the FAQ bot so this evaluator can be tuned.
"""

from evaluators.base import LLMJudgeEvaluator
from evaluators.types import EvaluationInput


class AbstentionEvaluator(LLMJudgeEvaluator):
    """
    LLM-based evaluator for appropriate abstention behavior in FAQ bot responses.
    """

    def __init__(self, pass_threshold: float = 0.7):
        """
        Initialize abstention evaluator.

        Args:
            pass_threshold: Minimum score to pass (default 0.7)
        """
        super().__init__(pass_threshold=pass_threshold)

    def build_judge_prompt(self, evaluation_input: EvaluationInput) -> str:
        """
        Build the LLM judge prompt for abstention behavior evaluation.

        Args:
            evaluation_input: Input containing question and bot response

        Returns:
            Formatted prompt string
        """
        # Provide context about what was retrieved (if any)
        retrieval_note = ""
        if evaluation_input.retrieved_docs is not None:
            doc_count = len(evaluation_input.retrieved_docs)
            if doc_count == 0:
                retrieval_note = "\n\nNOTE: No documents were retrieved for this question. Abstention may be appropriate."
            else:
                retrieval_note = f"\n\nNOTE: {doc_count} document(s) were retrieved for this question."

        prompt = f"""You are an abstention quality evaluator for a documentation FAQ bot. Evaluate whether the bot handles uncertainty and knowledge gaps appropriately.

USER QUESTION:
{evaluation_input.question}

BOT RESPONSE:
{evaluation_input.bot_response}
{retrieval_note}

Evaluate the response on the following criteria:

1. **Appropriate Confidence Calibration**: Does the bot's confidence level match what it should actually know?
   - Confidently answering when documentation clearly supports it → GOOD
   - Confidently answering when no relevant information exists → BAD (hallucination risk)
   - Abstaining or hedging when documentation is insufficient → GOOD
   - Refusing to answer when the question is clearly within scope → BAD (over-abstention)

2. **Abstention Quality** (if the bot abstains):
   - Is the abstention clear and honest? ("I don't have information on that in my documentation")
   - Does it suggest alternative resources or next steps for the user?
   - Is the abstention message helpful and not just a dead end?
   - Does it avoid pretending to answer with a hedged but hallucinated response?

3. **Scope Awareness**: Does the bot recognize when a question is outside its knowledge base?
   - Questions about undocumented topics should trigger abstention or a clear caveat.
   - Novel scenarios without documented precedent should be flagged explicitly.

4. **No False Confidence**: Does the bot avoid giving definitive answers without supporting evidence?
   - Phrases like "I'm confident that..." when no evidence exists are red flags.
   - Hedged speculation ("it might be...") without a source is still problematic.

Provide your evaluation as JSON:
{{
    "score": <float between 0.0 and 1.0, where 1.0 is perfectly calibrated abstention behavior>,
    "label": "<appropriate_abstention|appropriate_answer|over_abstention|hallucinated_answer>",
    "explanation": "<brief explanation of whether the bot handled uncertainty correctly, and why>"
}}

Score Guidelines:
- 1.0: Perfect — correctly answered with confidence OR correctly abstained when appropriate
- 0.8-0.9: Good calibration with minor hedging issues
- 0.6-0.7: Some miscalibration in confidence level
- 0.4-0.5: Answers when it should abstain (over-confident), or abstains when answer is obvious
- 0.0-0.3: Clear hallucination with false confidence, or systematic refusal of answerable questions
"""
        return prompt
