
"""
Policy Validator
=================
Validates model output against safety/quality policies BEFORE it is
returned to the user. Sits at the very end of the generation pipeline,
right before the response leaves brain/cortex and goes back through
the API layer.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional

logger = logging.getLogger(__name__)


class PolicySeverity(str, Enum):
    BLOCK = "block"        # never return this output, use fallback
    WARN = "warn"          # return output, but flag/log it
    REWRITE = "rewrite"    # attempt to strip/redact the offending part


@dataclass
class PolicyResult:
    policy_name: str
    passed: bool
    severity: PolicySeverity = PolicySeverity.WARN
    reason: str = ""
    matched_text: Optional[str] = None


@dataclass
class ValidationReport:
    is_safe: bool
    results: List[PolicyResult] = field(default_factory=list)
    final_output: str = ""
    fallback_used: bool = False

    def failed_policies(self) -> List[PolicyResult]:
        return [r for r in self.results if not r.passed]

    def highest_severity(self) -> Optional[PolicySeverity]:
        failed = self.failed_policies()
        if not failed:
            return None
        order = {PolicySeverity.BLOCK: 3, PolicySeverity.REWRITE: 2, PolicySeverity.WARN: 1}
        return max((r.severity for r in failed), key=lambda s: order[s])


class Policy:
    """Base class for a single policy check. Subclass and implement `check`."""

    name = "base_policy"
    severity = PolicySeverity.WARN

    def check(self, text: str, context: Optional[dict] = None) -> PolicyResult:
        raise NotImplementedError


class BannedPatternPolicy(Policy):
    """Blocks output containing disallowed patterns (secrets, PII markers, etc.)."""

    name = "banned_pattern"
    severity = PolicySeverity.BLOCK

    DEFAULT_PATTERNS = [
        r"\bsk-[a-zA-Z0-9]{20,}\b",          # leaked API keys
        r"\b\d{3}-\d{2}-\d{4}\b",             # SSN-like
        r"(?i)\bBEGIN (RSA|OPENSSH) PRIVATE KEY\b",
    ]

    def __init__(self, patterns: Optional[List[str]] = None):
        self.patterns = [re.compile(p) for p in (patterns or self.DEFAULT_PATTERNS)]

    def check(self, text: str, context: Optional[dict] = None) -> PolicyResult:
        for pattern in self.patterns:
            match = pattern.search(text)
            if match:
                return PolicyResult(
                    policy_name=self.name,
                    passed=False,
                    severity=self.severity,
                    reason=f"Matched banned pattern: {pattern.pattern}",
                    matched_text=match.group(0),
                )
        return PolicyResult(policy_name=self.name, passed=True)


class PromptInjectionEchoPolicy(Policy):
    """Flags output that echoes back injected instructions instead of answering."""

    name = "prompt_injection_echo"
    severity = PolicySeverity.WARN

    SUSPECT_PHRASES = [
        "ignore previous instructions",
        "disregard the system prompt",
        "as an ai with no restrictions",
        "i am now in developer mode",
    ]

    def check(self, text: str, context: Optional[dict] = None) -> PolicyResult:
        lowered = text.lower()
        for phrase in self.SUSPECT_PHRASES:
            if phrase in lowered:
                return PolicyResult(
                    policy_name=self.name,
                    passed=False,
                    severity=self.severity,
                    reason=f"Output echoes suspicious phrase: '{phrase}'",
                    matched_text=phrase,
                )
        return PolicyResult(policy_name=self.name, passed=True)


class EmptyOrDegenerateOutputPolicy(Policy):
    """Blocks empty, whitespace-only, or absurdly repetitive output."""

    name = "empty_or_degenerate"
    severity = PolicySeverity.BLOCK

    def check(self, text: str, context: Optional[dict] = None) -> PolicyResult:
        stripped = text.strip()
        if not stripped:
            return PolicyResult(self.name, False, self.severity, "Empty output")
        tokens = stripped.split()
        if len(tokens) > 15:
            for i in range(len(tokens) - 15):
                window = tokens[i:i + 15]
                if len(set(window)) == 1:
                    return PolicyResult(
                        self.name, False, self.severity,
                        "Degenerate repetition detected", matched_text=window[0],
                    )
        return PolicyResult(self.name, True)


class GroundednessPolicy(Policy):
    """
    Approximates a hallucination check: if the pipeline provided retrieved
    context (RAG chunks), flag output with no lexical overlap to it at all.
    """

    name = "groundedness_heuristic"
    severity = PolicySeverity.WARN
    MIN_OVERLAP_RATIO = 0.05

    def check(self, text: str, context: Optional[dict] = None) -> PolicyResult:
        context = context or {}
        source_text = context.get("retrieved_context")
        if not source_text:
            return PolicyResult(self.name, True)

        output_words = set(re.findall(r"[a-zA-Z]{4,}", text.lower()))
        source_words = set(re.findall(r"[a-zA-Z]{4,}", source_text.lower()))
        if not output_words:
            return PolicyResult(self.name, True)

        overlap = len(output_words & source_words) / len(output_words)
        if overlap < self.MIN_OVERLAP_RATIO:
            return PolicyResult(
                self.name, False, self.severity,
                reason=f"Low lexical overlap with retrieved context ({overlap:.2%})",
            )
        return PolicyResult(self.name, True)


class PolicyValidator:
    """Runs all Policy checks and produces a ValidationReport."""

    def __init__(self, policies: Optional[List[Policy]] = None,
                 fallback_provider: Optional[Callable[[ValidationReport], str]] = None):
        self.policies = policies or [
            BannedPatternPolicy(),
            PromptInjectionEchoPolicy(),
            EmptyOrDegenerateOutputPolicy(),
            GroundednessPolicy(),
        ]
        from brain.guardrails.fallback_handler import get_fallback_message  # <-- EDIT #1 already applied here
        self.fallback_provider = fallback_provider or get_fallback_message

    def validate(self, text: str, context: Optional[dict] = None) -> ValidationReport:
        results = [policy.check(text, context) for policy in self.policies]
        report = ValidationReport(is_safe=True, results=results, final_output=text)

        blocking_failures = [
            r for r in results if not r.passed and r.severity == PolicySeverity.BLOCK
        ]

        if blocking_failures:
            report.is_safe = False
            report.fallback_used = True
            report.final_output = self.fallback_provider(report)
            for r in blocking_failures:
                logger.warning("Policy '%s' BLOCKED output. Reason: %s", r.policy_name, r.reason)
        else:
            for r in [r for r in results if not r.passed]:
                logger.info("Policy '%s' flagged output (non-blocking). Reason: %s", r.policy_name, r.reason)

        return report

    def validate_result(self, result: dict, context: Optional[dict] = None) -> dict:
        """
        Wrapper matching CortexFlow's actual return shape:
        {"success": bool, "content": str, "metadata": dict, "processing_time": float}
        """
        if not result.get("success", True):
            return result

        content = result.get("content", "")
        report = self.validate(content, context=context)

        result["content"] = report.final_output
        result.setdefault("metadata", {})
        result["metadata"]["guardrails"] = {
            "is_safe": report.is_safe,
            "fallback_used": report.fallback_used,
            "failed_policies": [r.policy_name for r in report.failed_policies()],
        }
        result["_guardrails_report"] = report
        return result