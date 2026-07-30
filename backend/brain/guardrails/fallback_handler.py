"""
Fallback Handler
=================
Chooses a user-facing fallback message when policy_validator.py blocks
an output.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from brain.guardrails.policy_validator import ValidationReport, PolicySeverity  # noqa: F401

FALLBACK_MESSAGES = {
    "banned_pattern": (
        "I can't share that response because it may contain sensitive or "
        "restricted information. Could you rephrase your request?"
    ),
    "prompt_injection_echo": (
        "I wasn't able to produce a reliable answer for that request. "
        "Could you try rephrasing it?"
    ),
    "empty_or_degenerate": (
        "I ran into trouble generating a response. Please try again, "
        "or rephrase your question."
    ),
    "groundedness_heuristic": (
        "I don't have enough verified information to answer that confidently. "
        "Could you provide more detail or check with another source?"
    ),
}

DEFAULT_FALLBACK = (
    "I'm not able to provide a response to that right now. "
    "Please try rephrasing your question, or contact support if this continues."
)


def get_fallback_message(report: "ValidationReport") -> str:
    blocking = [r for r in report.results if not r.passed and r.severity.value == "block"]
    for result in blocking:
        if result.policy_name in FALLBACK_MESSAGES:
            return FALLBACK_MESSAGES[result.policy_name]
    return DEFAULT_FALLBACK