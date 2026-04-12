"""
Readability and Length Evaluator

Type: RULE-BASED

Evaluates the readability and length of bot responses using deterministic metrics:
- Response length (not too short, not too long)
- Sentence complexity
- Reading level (Flesch-Kincaid)
- Paragraph structure

This is a rule-based evaluator that doesn't require LLM calls.

For Zoe bot: Ensures responses are accessible and easy to read for users
who may be in emotional distress.

For FAQ bot: Ensures documentation answers are concise and scannable.
"""

import re
from evaluators.base import BaseEvaluator
from evaluators.types import EvaluationInput, EvaluationResult, EvaluatorType


class ReadabilityLengthEvaluator(BaseEvaluator):
    """
    Rule-based evaluator for readability and length.
    """

    evaluator_type = EvaluatorType.RULE_BASED

    def __init__(
        self,
        pass_threshold: float = 0.7,
        min_words: int = 20,
        max_words: int = 300,
        max_reading_level: float = 12.0
    ):
        """
        Initialize readability evaluator.

        Args:
            pass_threshold: Minimum score to pass
            min_words: Minimum word count
            max_words: Maximum word count
            max_reading_level: Maximum Flesch-Kincaid grade level
        """
        super().__init__(pass_threshold=pass_threshold)
        self.min_words = min_words
        self.max_words = max_words
        self.max_reading_level = max_reading_level

    def evaluate(self, evaluation_input: EvaluationInput) -> EvaluationResult:
        """
        Evaluate readability using rule-based metrics.

        Args:
            evaluation_input: Input containing bot response

        Returns:
            EvaluationResult with score and metrics
        """
        response = evaluation_input.bot_response

        # Calculate metrics
        word_count = self._count_words(response)
        sentence_count = self._count_sentences(response)
        syllable_count = self._count_syllables(response)

        # Calculate Flesch-Kincaid Reading Ease and Grade Level
        flesch_score = self._calculate_flesch_reading_ease(
            word_count, sentence_count, syllable_count
        )
        grade_level = self._calculate_flesch_kincaid_grade(
            word_count, sentence_count, syllable_count
        )

        # Score components (each 0.0 to 1.0)
        length_score = self._score_length(word_count)
        readability_score = self._score_readability(grade_level)
        sentence_score = self._score_sentence_structure(response, sentence_count)

        # Weighted average
        overall_score = (
            length_score * 0.4 +
            readability_score * 0.4 +
            sentence_score * 0.2
        )

        # Determine label
        if overall_score >= 0.8:
            label = "excellent"
        elif overall_score >= 0.6:
            label = "good"
        else:
            label = "needs_improvement"

        # Build explanation
        explanation = self._build_explanation(
            word_count, grade_level, flesch_score, overall_score
        )

        return self._create_result(
            score=overall_score,
            explanation=explanation,
            label=label,
            metadata={
                "word_count": word_count,
                "sentence_count": sentence_count,
                "flesch_score": round(flesch_score, 1),
                "grade_level": round(grade_level, 1),
                "length_score": round(length_score, 2),
                "readability_score": round(readability_score, 2),
                "sentence_score": round(sentence_score, 2)
            }
        )

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        words = re.findall(r'\b\w+\b', text)
        return len(words)

    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r'[.!?]+', text)
        return max(1, len([s for s in sentences if s.strip()]))

    def _count_syllables(self, text: str) -> int:
        """
        Estimate syllable count (simple heuristic).
        Count vowel groups as syllables.
        """
        text = text.lower()
        text = re.sub(r'[^a-z]', ' ', text)
        words = text.split()

        syllable_count = 0
        for word in words:
            # Count vowel groups
            syllables = len(re.findall(r'[aeiouy]+', word))
            # Handle silent 'e'
            if word.endswith('e') and syllables > 1:
                syllables -= 1
            syllable_count += max(1, syllables)

        return max(1, syllable_count)

    def _calculate_flesch_reading_ease(
        self, words: int, sentences: int, syllables: int
    ) -> float:
        """
        Calculate Flesch Reading Ease score.
        Score ranges: 90-100 (very easy) to 0-30 (very difficult)
        """
        if words == 0 or sentences == 0:
            return 0.0

        score = (
            206.835
            - 1.015 * (words / sentences)
            - 84.6 * (syllables / words)
        )
        return max(0.0, min(100.0, score))

    def _calculate_flesch_kincaid_grade(
        self, words: int, sentences: int, syllables: int
    ) -> float:
        """
        Calculate Flesch-Kincaid Grade Level.
        Returns U.S. school grade level needed to understand the text.
        """
        if words == 0 or sentences == 0:
            return 0.0

        grade = (
            0.39 * (words / sentences)
            + 11.8 * (syllables / words)
            - 15.59
        )
        return max(0.0, grade)

    def _score_length(self, word_count: int) -> float:
        """
        Score response length.
        Ideal: 50-200 words for conversational responses.
        """
        if word_count < self.min_words:
            # Too short
            return max(0.0, word_count / self.min_words)
        elif word_count > self.max_words:
            # Too long - penalty increases with length
            excess = word_count - self.max_words
            penalty = min(0.5, excess / self.max_words)
            return max(0.0, 1.0 - penalty)
        else:
            # Ideal range
            return 1.0

    def _score_readability(self, grade_level: float) -> float:
        """
        Score reading level.
        Target: 8th grade or below for accessibility.
        """
        if grade_level <= 8.0:
            return 1.0
        elif grade_level <= self.max_reading_level:
            # Gradual penalty up to max
            penalty = (grade_level - 8.0) / (self.max_reading_level - 8.0)
            return max(0.3, 1.0 - penalty * 0.5)
        else:
            # Too difficult
            return 0.3

    def _score_sentence_structure(self, text: str, sentence_count: int) -> float:
        """
        Score sentence structure.
        Look for:
        - Reasonable sentence count
        - Paragraph breaks (good for scannability)
        - Not too many very short or very long sentences
        """
        words = self._count_words(text)
        if sentence_count == 0 or words == 0:
            return 0.0

        avg_words_per_sentence = words / sentence_count

        # Ideal: 15-20 words per sentence
        if 10 <= avg_words_per_sentence <= 25:
            structure_score = 1.0
        elif avg_words_per_sentence < 10:
            # Too choppy
            structure_score = max(0.5, avg_words_per_sentence / 10)
        else:
            # Too long
            structure_score = max(0.5, 25 / avg_words_per_sentence)

        # Bonus for paragraph breaks (better scannability)
        paragraph_count = text.count('\n\n') + 1
        if paragraph_count > 1 and words > 100:
            structure_score = min(1.0, structure_score + 0.1)

        return structure_score

    def _build_explanation(
        self, word_count: int, grade_level: float, flesch_score: float, overall_score: float
    ) -> str:
        """Build human-readable explanation."""
        parts = []

        # Word count feedback
        if word_count < self.min_words:
            parts.append(f"Response is too short ({word_count} words)")
        elif word_count > self.max_words:
            parts.append(f"Response is too long ({word_count} words)")
        else:
            parts.append(f"Good length ({word_count} words)")

        # Reading level feedback
        if grade_level <= 8:
            parts.append(f"Easy to read (grade {grade_level:.1f})")
        elif grade_level <= 12:
            parts.append(f"Moderate difficulty (grade {grade_level:.1f})")
        else:
            parts.append(f"Complex language (grade {grade_level:.1f})")

        # Overall assessment
        if overall_score >= 0.8:
            parts.append("Excellent readability")
        elif overall_score >= 0.6:
            parts.append("Good readability")
        else:
            parts.append("Needs improvement for accessibility")

        return ". ".join(parts) + "."
