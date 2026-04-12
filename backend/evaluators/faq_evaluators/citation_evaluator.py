"""
Citation Evaluator

Type: LLM-BASED

Evaluates whether the FAQ bot's response includes proper citations and references
to source documents when making claims.

Key checks:
- Are citations present when the answer draws from documentation?
- Do citations match the provided retrieved documents?
- Are citations specific enough to be useful?
- Are there no phantom/fabricated citations?

For FAQ bot: Critical for maintaining trust and verifiability of answers.
Users should be able to trace claims back to source documentation.

TODO (FAQ bot integration):
- Pass retrieved_docs with document IDs for citation cross-checking.
- Agree on a citation format (e.g., "[doc_id]", "(Source: X)") and adjust the prompt.
- Build test cases with expected citation patterns.
"""

from evaluators.base import LLMJudgeEvaluator
from evaluators.types import EvaluationInput


class CitationEvaluator(LLMJudgeEvaluator):
    """
    LLM-based evaluator for citation quality in FAQ bot responses.

    Requires retrieved_docs in EvaluationInput for full evaluation.
    If no retrieved_docs are provided, evaluates based on citation presence alone.
    """

    def __init__(self, pass_threshold: float = 0.7):
        """
        Initialize citation evaluator.

        Args:
            pass_threshold: Minimum citation quality score to pass (default 0.7)
        """
        super().__init__(pass_threshold=pass_threshold)

    def build_judge_prompt(self, evaluation_input: EvaluationInput) -> str:
        """
        Build the LLM judge prompt for citation quality evaluation.

        Args:
            evaluation_input: Input with bot_response and optionally retrieved_docs

        Returns:
            Formatted prompt string
        """
        # Build source context from retrieved docs if available
        source_context = ""
        if evaluation_input.retrieved_docs:
            source_context = "\n\nAVAILABLE SOURCE DOCUMENTS:\n"
            for i, doc in enumerate(evaluation_input.retrieved_docs, 1):
                doc_id = doc.get("id", f"doc_{i}")
                content = doc.get("content", doc.get("text", ""))[:300]
                source_context += f"[{doc_id}]: {content}...\n"
        else:
            source_context = "\n\nNOTE: No source documents provided. Evaluate based on citation presence only."

        prompt = f"""You are a citation quality evaluator for a documentation FAQ bot. Evaluate whether the response properly cites its sources.

USER QUESTION:
{evaluation_input.question}

BOT RESPONSE:
{evaluation_input.bot_response}
{source_context}

Evaluate the response on the following criteria:

1. **Citation Presence**: When the response makes factual claims from documentation, are sources cited?
   - Acceptable formats: "[doc_id]", "(Source: X)", "According to [document]", "per the documentation", etc.
   - Responses with only general knowledge may not require formal citations.
   - Responses that clearly draw from specific documentation SHOULD cite sources.

2. **Citation Accuracy** (only if source documents are provided):
   - Do citations reference documents that actually exist in the provided sources?
   - Do cited documents actually contain the cited information?
   - No phantom or fabricated document references.

3. **Citation Usefulness**: Are citations specific enough to be actionable?
   - Vague "see documentation" is less useful than specific document references.
   - Users should be able to verify cited claims.

4. **Appropriate Abstention**: If no relevant source exists, does the response acknowledge this
   rather than citing phantom documents?

Provide your evaluation as JSON:
{{
    "score": <float between 0.0 and 1.0, where 1.0 is perfectly cited>,
    "label": "<well_cited|partially_cited|uncited|phantom_citations>",
    "explanation": "<brief explanation of citation quality, noting any missing or fabricated citations>"
}}

Score Guidelines:
- 1.0: All factual claims properly cited with accurate, specific source references
- 0.8-0.9: Good citations with minor omissions or vague references
- 0.6-0.7: Some claims cited, others not; or only vague citations present
- 0.4-0.5: Minimal citations despite clearly drawing from documentation
- 0.0-0.3: No citations when clearly needed, or phantom/fabricated citations present
"""
        return prompt
