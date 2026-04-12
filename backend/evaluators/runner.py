"""
Evaluator Runner

Offline evaluation runner for Zoe and FAQ bot responses.

Usage (run from backend/ directory):
    # Run common evaluators against Zoe using pre-baked test cases
    python -m evaluators.runner --bot zoe --input evaluators/test_cases.json

    # Run all evaluators (common + FAQ) against FAQ bot
    python -m evaluators.runner --bot faq --input evaluators/test_cases.json

    # Get live responses from Zoe instead of using pre-baked ones
    python -m evaluators.runner --bot zoe --input evaluators/test_cases.json --live

    # Save results to a JSON file in addition to printing
    python -m evaluators.runner --bot zoe --input evaluators/test_cases.json --output results.json

Test case schema (see evaluators/test_cases.json for examples):
    {
        "id": "zoe_001",
        "question": "...",               # Required
        "bot_type": "zoe",               # "zoe" or "faq"
        "bot_response": "...",           # Optional: pre-baked response (offline mode)
        "expected_answer": "...",        # Optional: for FAQExactnessEvaluator
        "user_context": {"ace_score": 3},# Optional: user metadata for context-aware evaluators
        "retrieved_docs": [...],         # Optional: for FAQ evaluators (retrieval/faithfulness)
        "metadata": {}                   # Optional: for policy_reference, etc.
    }

How bot_response works:
    - If bot_response is present in the test case → used directly (offline mode).
    - If bot_response is absent AND --live is set → calls the bot adapter for a live response.
    - If bot_response is absent AND --live is not set → test case is skipped with a warning.

How to add the FAQ bot later:
    1. Implement FAQBotAdapter.get_response() in evaluators/zoe_adapter.py.
    2. Add FAQ test cases (bot_type="faq") to test_cases.json.
    3. Run: python -m evaluators.runner --bot faq --input evaluators/test_cases.json
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Load .env before importing anything that needs API keys
from dotenv import load_dotenv
load_dotenv()

from evaluators.types import BotType, EvaluationInput, EvaluationResult, TestCase
from evaluators.common_evaluators import (
    SafetyHarmEvaluator,
    FactualityHallucinationRiskEvaluator,
    InstructionFollowingRelevanceEvaluator,
    EmpathyToneEvaluator,
    ReadabilityLengthEvaluator,
)
from evaluators.faq_evaluators import (
    RetrievalPrecisionRecallEvaluator,
    AnswerFaithfulnessEvaluator,
    CitationEvaluator,
    FAQExactnessEvaluator,
    AbstentionEvaluator,
    PolicyConsistencyEvaluator,
)

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Evaluator registries
# ---------------------------------------------------------------------------

COMMON_EVALUATORS = [
    SafetyHarmEvaluator(),
    FactualityHallucinationRiskEvaluator(),
    InstructionFollowingRelevanceEvaluator(),
    EmpathyToneEvaluator(),
    ReadabilityLengthEvaluator(),
]

FAQ_ONLY_EVALUATORS = [
    RetrievalPrecisionRecallEvaluator(),
    AnswerFaithfulnessEvaluator(),
    CitationEvaluator(),
    FAQExactnessEvaluator(),
    AbstentionEvaluator(),
    PolicyConsistencyEvaluator(),
]


def get_evaluators_for_bot(bot_type: str) -> List:
    """Return the list of evaluators appropriate for the given bot type."""
    if bot_type == "zoe":
        return COMMON_EVALUATORS
    elif bot_type == "faq":
        return COMMON_EVALUATORS + FAQ_ONLY_EVALUATORS
    else:
        raise ValueError(f"Unknown bot type: {bot_type!r}. Use 'zoe' or 'faq'.")


# ---------------------------------------------------------------------------
# Test case loading
# ---------------------------------------------------------------------------

def load_test_cases(input_path: str, bot_type: str) -> List[Dict[str, Any]]:
    """
    Load test cases from a JSON file.

    Filters to only cases matching bot_type (or all if no bot_type field).

    Args:
        input_path: Path to test_cases.json
        bot_type: "zoe" or "faq"

    Returns:
        List of raw test case dicts
    """
    path = Path(input_path)
    if not path.exists():
        print(f"\n[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    with open(path, "r") as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        print(f"\n[ERROR] test_cases.json must be a JSON array. Got: {type(raw).__name__}")
        sys.exit(1)

    # Filter by bot_type
    cases = [tc for tc in raw if tc.get("bot_type", bot_type) == bot_type]

    if not cases:
        print(f"\n[WARNING] No test cases found for bot_type='{bot_type}' in {input_path}")
        print(f"  Available bot_types: {sorted(set(tc.get('bot_type', 'zoe') for tc in raw))}")

    return cases


# ---------------------------------------------------------------------------
# Live response acquisition
# ---------------------------------------------------------------------------

async def get_live_response(bot_type: str, test_case: Dict[str, Any]) -> str:
    """
    Call the appropriate bot adapter to get a live response.

    Args:
        bot_type: "zoe" or "faq"
        test_case: Raw test case dict

    Returns:
        Bot response string
    """
    question = test_case["question"]
    user_context = test_case.get("user_context") or {}

    if bot_type == "zoe":
        from evaluators.zoe_adapter import ZoeBotAdapter
        adapter = ZoeBotAdapter()
        return await adapter.get_response(question, user_context)

    elif bot_type == "faq":
        from evaluators.zoe_adapter import FAQBotAdapter
        adapter = FAQBotAdapter()
        return await adapter.get_response(question, user_context)

    raise ValueError(f"No adapter for bot_type: {bot_type!r}")


# ---------------------------------------------------------------------------
# Evaluation execution
# ---------------------------------------------------------------------------

def run_evaluators(
    evaluators: List,
    evaluation_input: EvaluationInput,
) -> List[EvaluationResult]:
    """
    Run all evaluators against a single evaluation input.

    Args:
        evaluators: List of evaluator instances
        evaluation_input: Standardized input

    Returns:
        List of EvaluationResult objects
    """
    results = []
    for evaluator in evaluators:
        try:
            result = evaluator.evaluate(evaluation_input)
            results.append(result)
        except Exception as exc:
            # Never let one evaluator crash the whole run
            logger.error(f"Evaluator {evaluator.__class__.__name__} failed: {exc}")
            results.append(EvaluationResult(
                evaluator_name=evaluator.name,
                score=0.0,
                passed=False,
                label="error",
                explanation=f"Evaluator error: {exc}",
                metadata={"error": str(exc)},
            ))
    return results


# ---------------------------------------------------------------------------
# Terminal output
# ---------------------------------------------------------------------------

PASS_SYMBOL = "✓"
FAIL_SYMBOL = "✗"
WIDTH = 72


def _bar(char: str = "─", width: int = WIDTH) -> str:
    return char * width


def print_header(bot_type: str, case_count: int, evaluator_count: int) -> None:
    print()
    print(_bar("═"))
    print("  ThinkLife Evaluator Runner")
    print(_bar("═"))
    print(f"  Bot:        {bot_type}")
    print(f"  Test cases: {case_count}")
    print(f"  Evaluators: {evaluator_count}")
    print(_bar())


def print_case_results(case_id: str, question: str, results: List[EvaluationResult]) -> None:
    preview = question[:60] + ("…" if len(question) > 60 else "")
    print(f"\n[{case_id}] \"{preview}\"")
    for r in results:
        symbol = PASS_SYMBOL if r.passed else FAIL_SYMBOL
        label_str = f"| {r.label:<22}" if r.label else ""
        name_col = f"{r.evaluator_name:<32}"
        print(f"  {symbol} {name_col} score={r.score:.2f}  {'PASS' if r.passed else 'FAIL'}  {label_str}")
        # Print truncated explanation on a second line
        if r.explanation:
            expl = r.explanation[:80] + ("…" if len(r.explanation) > 80 else "")
            print(f"    → {expl}")


def print_summary(all_case_results: List[Tuple[str, List[EvaluationResult]]]) -> None:
    """Print aggregated summary table."""
    print()
    print(_bar("═"))
    print("  SUMMARY")
    print(_bar("═"))

    # Aggregate per evaluator
    evaluator_stats: Dict[str, Dict] = {}
    total_checks = 0
    total_passed = 0

    for _case_id, results in all_case_results:
        for r in results:
            name = r.evaluator_name
            if name not in evaluator_stats:
                evaluator_stats[name] = {"passed": 0, "total": 0, "score_sum": 0.0}
            evaluator_stats[name]["total"] += 1
            evaluator_stats[name]["score_sum"] += r.score
            if r.passed:
                evaluator_stats[name]["passed"] += 1
            total_checks += 1
            if r.passed:
                total_passed += 1

    overall_rate = total_passed / total_checks * 100 if total_checks > 0 else 0.0

    print(f"  Total cases:  {len(all_case_results)}")
    print(f"  Total checks: {total_checks}")
    print(f"  Passed:       {total_passed} ({overall_rate:.1f}%)")
    print(f"  Failed:       {total_checks - total_passed} ({100 - overall_rate:.1f}%)")
    print()
    print(f"  {'Evaluator':<34} {'Pass':<8} {'Rate':<10} {'Avg Score'}")
    print(f"  {_bar('-', 60)}")
    for name, stats in evaluator_stats.items():
        passed = stats["passed"]
        total = stats["total"]
        avg = stats["score_sum"] / total if total > 0 else 0.0
        rate = passed / total * 100 if total > 0 else 0.0
        print(f"  {name:<34} {passed}/{total:<6}  {rate:>5.1f}%    {avg:.2f}")

    print(_bar("═"))
    if overall_rate >= 90:
        print("  Result: EXCELLENT — framework looks healthy.")
    elif overall_rate >= 70:
        print("  Result: ACCEPTABLE — review failed cases above.")
    else:
        print("  Result: NEEDS ATTENTION — significant failures detected.")
    print(_bar("═"))
    print()


# ---------------------------------------------------------------------------
# Output serialization
# ---------------------------------------------------------------------------

def build_output_dict(
    bot_type: str,
    all_case_results: List[Tuple[str, List[EvaluationResult]]],
    test_cases: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build a serializable results dict for --output."""
    evaluator_stats: Dict[str, Dict] = {}
    results_by_case = []

    for case_id, results in all_case_results:
        case_dict = {
            "case_id": case_id,
            "results": [r.to_dict() for r in results],
        }
        results_by_case.append(case_dict)

        for r in results:
            name = r.evaluator_name
            if name not in evaluator_stats:
                evaluator_stats[name] = {"passed": 0, "total": 0, "score_sum": 0.0}
            evaluator_stats[name]["total"] += 1
            evaluator_stats[name]["score_sum"] += r.score
            if r.passed:
                evaluator_stats[name]["passed"] += 1

    for name, stats in evaluator_stats.items():
        total = stats["total"]
        stats["avg_score"] = round(stats["score_sum"] / total, 3) if total > 0 else 0.0
        stats["pass_rate"] = round(stats["passed"] / total, 3) if total > 0 else 0.0

    total_checks = sum(s["total"] for s in evaluator_stats.values())
    total_passed = sum(s["passed"] for s in evaluator_stats.values())

    return {
        "meta": {
            "bot_type": bot_type,
            "run_at": datetime.now().isoformat(),
            "total_cases": len(all_case_results),
            "total_checks": total_checks,
            "total_passed": total_passed,
            "overall_pass_rate": round(total_passed / total_checks, 3) if total_checks > 0 else 0.0,
        },
        "by_evaluator": evaluator_stats,
        "by_case": results_by_case,
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ThinkLife offline evaluator runner.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--bot",
        required=True,
        choices=["zoe", "faq"],
        help="Which bot to evaluate: 'zoe' or 'faq'",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to test_cases.json (relative to CWD or absolute)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to save results JSON (e.g. results.json)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        default=False,
        help=(
            "Call the bot live for test cases without a pre-baked bot_response. "
            "Requires all bot dependencies to be available."
        ),
    )
    return parser.parse_args()


def check_api_key() -> None:
    """Warn if OPENAI_API_KEY is not set (LLM-based evaluators will fail)."""
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "\n[WARNING] OPENAI_API_KEY is not set. LLM-based evaluators will fail.\n"
            "  Set it in your .env file or environment before running.\n"
        )


def main() -> None:
    args = parse_args()
    check_api_key()

    # Load test cases
    raw_cases = load_test_cases(args.input, args.bot)
    if not raw_cases:
        sys.exit(0)

    evaluators = get_evaluators_for_bot(args.bot)
    print_header(args.bot, len(raw_cases), len(evaluators))

    all_case_results: List[Tuple[str, List[EvaluationResult]]] = []

    for raw_case in raw_cases:
        case_id = raw_case.get("id", "unknown")
        question = raw_case.get("question", "")

        # Resolve bot_response
        bot_response = raw_case.get("bot_response")

        if not bot_response:
            if args.live:
                print(f"\n  [LIVE] Getting response for {case_id}...")
                bot_response = asyncio.run(get_live_response(args.bot, raw_case))
            else:
                print(
                    f"\n  [SKIP] {case_id} — no bot_response in test case and --live not set. "
                    "Add a bot_response field or pass --live."
                )
                continue

        # Build EvaluationInput
        bot_type_enum = BotType.ZOE if args.bot == "zoe" else BotType.FAQ
        evaluation_input = EvaluationInput(
            question=question,
            bot_response=bot_response,
            retrieved_docs=raw_case.get("retrieved_docs"),
            expected_answer=raw_case.get("expected_answer"),
            user_context=raw_case.get("user_context"),
            metadata=raw_case.get("metadata"),
            bot_type=bot_type_enum,
            session_id=raw_case.get("session_id"),
        )

        # Run evaluators
        results = run_evaluators(evaluators, evaluation_input)
        all_case_results.append((case_id, results))

        print_case_results(case_id, question, results)

    if not all_case_results:
        print("\nNo cases were evaluated. Check your input file and flags.")
        return

    print_summary(all_case_results)

    # Optionally save results
    if args.output:
        output_data = build_output_dict(args.bot, all_case_results, raw_cases)
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"  Results saved to: {output_path.resolve()}\n")


if __name__ == "__main__":
    main()
