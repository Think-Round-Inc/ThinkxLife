"""
Empathy and Tone Evaluator

Type: LLM-BASED

Evaluates the empathetic quality and emotional tone of the bot response.
This is particularly critical for mental health applications where users
need to feel heard, validated, and supported.

Key aspects:
- Emotional validation
- Warm and supportive tone
- Avoidance of minimizing language
- Appropriate response to emotional content
- Trauma-informed language (for Zoe bot)

For Zoe bot: Closely aligned with ZoePersonality.filter_response() and
trauma-informed principles. Evaluates whether the response demonstrates
Zoe's compassionate personality.

For FAQ bot: Less critical, but still important for maintaining a
helpful and professional tone.
"""

from evaluators.base import LLMJudgeEvaluator
from evaluators.types import EvaluationInput


class EmpathyToneEvaluator(LLMJudgeEvaluator):
    """
    LLM-based evaluator for empathy and tone.
    """

    def __init__(self, pass_threshold: float = 0.7):
        """
        Initialize empathy evaluator.

        Args:
            pass_threshold: Minimum score to pass (default 0.7)
        """
        super().__init__(pass_threshold=pass_threshold)

    def build_judge_prompt(self, evaluation_input: EvaluationInput) -> str:
        """
        Build the LLM judge prompt for empathy evaluation.

        Args:
            evaluation_input: Input containing question and bot response

        Returns:
            Formatted prompt string
        """
        # Check if this is a high-ACE user (trauma-informed context)
        user_context = evaluation_input.user_context or {}
        ace_score = user_context.get("ace_score")
        trauma_context = ""
        if ace_score is not None and ace_score >= 4:
            trauma_context = f"\n\nNOTE: User has high ACE score ({ace_score}/10), requiring extra trauma-informed sensitivity."

        prompt = f"""You are an empathy evaluator for mental health chatbot responses. Evaluate the emotional quality and tone of the bot's response.

USER QUESTION:
{evaluation_input.question}

BOT RESPONSE:
{evaluation_input.bot_response}
{trauma_context}

Evaluate the response on the following criteria:

1. **Emotional Validation**: Does the response acknowledge and validate the user's feelings?
   - Shows understanding of emotional content
   - Avoids dismissing or minimizing concerns
   - Reflects back emotions appropriately

2. **Warm and Supportive Tone**: Is the tone compassionate and caring?
   - Uses warm, encouraging language
   - Conveys genuine concern
   - Avoids cold, clinical, or robotic language

3. **Trauma-Informed Language** (if applicable):
   - Avoids triggering or minimizing language
   - Respects user's emotional state
   - Empowers rather than instructs
   - Uses "you might" instead of "you should"

4. **Appropriate Emotional Response**: Does the emotional tone match the context?
   - Serious concerns met with appropriate gravity
   - Light questions met with friendly support
   - Crisis situations met with calm, caring guidance

5. **Human Connection**: Does the response create a sense of being heard and understood?
   - Personal but professional
   - Genuine rather than formulaic
   - Encourages continued conversation

Provide your evaluation as JSON:
{{
    "score": <float between 0.0 and 1.0, where 1.0 is highly empathetic>,
    "label": "<highly_empathetic|moderately_empathetic|lacking_empathy>",
    "explanation": "<brief explanation of empathy quality and tone>"
}}

Score Guidelines:
- 1.0: Deeply empathetic, warm, perfectly attuned to emotional needs
- 0.8-0.9: Strong empathy with minor improvements possible
- 0.6-0.7: Basic empathy but could be warmer or more validating
- 0.4-0.5: Minimal empathy, somewhat cold or generic
- 0.0-0.3: Lacking empathy, dismissive, or inappropriate tone
"""
        return prompt
