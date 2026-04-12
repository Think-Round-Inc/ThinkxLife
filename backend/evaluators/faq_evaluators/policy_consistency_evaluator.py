"""
Policy Consistency Evaluator

Type: LLM-BASED

Evaluates whether the FAQ bot's responses are consistent with organizational
policies, guidelines, and rules. Important for FAQ bots operating in regulated
or policy-driven environments where incorrect policy guidance can cause harm.

Two things this catches:
1. Policy violations: Bot says something is allowed/required when policy says otherwise.
2. Incomplete policy coverage: Bot omits critical caveats, exceptions, or constraints.

Policy reference can be supplied via:
- evaluation_input.metadata["policy_reference"]  — explicit policy text string
- evaluation_input.retrieved_docs                — policy documents from retrieval

If no policy reference is available, the evaluator judges based on general best
practices and the context of the question.

TODO (FAQ bot integration):
- Define the organizational policy scope for the FAQ bot.
- Add policy_reference to test cases covering policy-sensitive questions.
- Build a dedicated policy document corpus for retrieval (separate from general FAQ docs).
- Consider a higher pass threshold (0.9) for safety-critical policy domains.
"""

from evaluators.base import LLMJudgeEvaluator
from evaluators.types import EvaluationInput


class PolicyConsistencyEvaluator(LLMJudgeEvaluator):
    """
    LLM-based evaluator for policy consistency in FAQ bot responses.

    Uses a higher default threshold (0.8) since policy violations can be consequential.
    """

    def __init__(self, pass_threshold: float = 0.8):
        """
        Initialize policy consistency evaluator.

        Args:
            pass_threshold: Minimum score to pass (default 0.8 — high bar for policy)
        """
        super().__init__(pass_threshold=pass_threshold)

    def build_judge_prompt(self, evaluation_input: EvaluationInput) -> str:
        """
        Build the LLM judge prompt for policy consistency evaluation.

        Args:
            evaluation_input: Input with bot_response and optional policy reference

        Returns:
            Formatted prompt string
        """
        policy_context = self._extract_policy_context(evaluation_input)

        prompt = f"""You are a policy consistency evaluator for a documentation FAQ bot. Evaluate whether the bot's response aligns with organizational policies and guidelines.

USER QUESTION:
{evaluation_input.question}

BOT RESPONSE:
{evaluation_input.bot_response}

{policy_context}

Evaluate the response on the following criteria:

1. **Policy Alignment**: Does the response accurately reflect stated policies?
   - No contradictions with documented rules, procedures, or guidelines
   - Correct interpretation of what is/isn't allowed or required
   - Accurate representation of policy intent, not just literal wording

2. **Sensitive Information Handling**: Is policy-sensitive content handled correctly?
   - Personal data and privacy policies respected
   - Confidentiality or access restrictions accurately represented
   - Security-relevant policy details not exposed inappropriately

3. **Policy Completeness**: Does the response include all relevant policy constraints?
   - Important caveats, exceptions, or conditions mentioned
   - No critical omissions that could lead to policy violations
   - Edge cases or special circumstances flagged when relevant

4. **Consistency Across Policies**: If multiple policies apply, are they consistently represented?
   - No contradictions between referenced policies
   - Policy hierarchy or precedence respected

5. **Clear Attribution**: Are policy statements attributed appropriately?
   - Policies presented as organizational rules, not the bot's opinion
   - Source of policies indicated when possible

Provide your evaluation as JSON:
{{
    "score": <float between 0.0 and 1.0, where 1.0 is fully policy-consistent>,
    "label": "<policy_compliant|minor_inconsistency|policy_violation>",
    "explanation": "<brief explanation identifying any policy inconsistencies, violations, or missing constraints>"
}}

Score Guidelines:
- 1.0: Fully consistent with all applicable policies, complete and accurate
- 0.8-0.9: Consistent with minor ambiguities or incomplete coverage of edge cases
- 0.6-0.7: Some inconsistency with policy guidance or notable omissions
- 0.4-0.5: Notable policy violations or direct contradictions
- 0.0-0.3: Clear policy violations that could mislead users into non-compliance
"""
        return prompt

    def _extract_policy_context(self, evaluation_input: EvaluationInput) -> str:
        """
        Extract policy reference from metadata or retrieved docs.

        Priority:
        1. Explicit policy_reference in metadata (most precise)
        2. Retrieved docs (may contain policy documents)
        3. Fallback to general best practices note

        Args:
            evaluation_input: Evaluation input

        Returns:
            Formatted policy context string for the prompt
        """
        metadata = evaluation_input.metadata or {}
        policy_ref = metadata.get("policy_reference")

        if policy_ref:
            return f"POLICY REFERENCE:\n{policy_ref}"

        if evaluation_input.retrieved_docs:
            context = "POLICY DOCUMENTS (from retrieved context):\n"
            for i, doc in enumerate(evaluation_input.retrieved_docs, 1):
                doc_id = doc.get("id", f"doc_{i}")
                content = doc.get("content", doc.get("text", ""))[:400]
                context += f"[{doc_id}]: {content}...\n"
            return context

        return (
            "NOTE: No explicit policy reference provided. "
            "Evaluate based on general organizational best practices, "
            "common compliance standards, and the context of the question."
        )
