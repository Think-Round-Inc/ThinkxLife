"""
Latency Evaluator

Monitors and evaluates response time performance with LangFuse observability
for tracking performance metrics over time.
"""

import logging
import statistics
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Conditional Langfuse import
try:
    from langfuse import observe
except ImportError:
    def observe(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator


class LatencyEvaluator:
    """Evaluates response time performance"""

    def __init__(self):
        self.response_times: List[float] = []
        self.thresholds = {
            "excellent": 2.0,
            "good": 5.0,
            "acceptable": 10.0,
            "poor": float('inf')
        }

    @observe(name="evaluate_latency")
    async def evaluate(
        self,
        start_time: float,
        end_time: float,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Evaluate response latency"""
        latency = end_time - start_time
        self.response_times.append(latency)
        
        category, score = self._categorize_latency(latency)
        stats = self._calculate_statistics()
        
        if category == "poor":
            logger.warning(f"Poor latency: {latency:.2f}s (acceptable: {self.thresholds['acceptable']}s)")
        
        return {
            "response_latency_seconds": round(latency, 3),
            "performance_score": score,
            "performance_category": category,
            "statistics": stats,
            "thresholds": self.thresholds,
            "evaluation_timestamp": datetime.now().isoformat(),
            "evaluator": "latency"
        }

    def _categorize_latency(self, latency: float) -> tuple[str, float]:
        if latency <= self.thresholds["excellent"]: return "excellent", 1.0
        if latency <= self.thresholds["good"]: return "good", 0.8
        if latency <= self.thresholds["acceptable"]: return "acceptable", 0.6
        return "poor", 0.3

    def _calculate_statistics(self) -> Dict[str, Any]:
        if not self.response_times: return {}
        
        recent = self.response_times[-100:]
        stats = {
            "total_evaluations": len(self.response_times),
            "average_latency_recent": round(statistics.mean(recent), 3),
            "median_latency_recent": round(statistics.median(recent), 3),
            "min_latency_recent": round(min(recent), 3),
            "max_latency_recent": round(max(recent), 3),
        }
        
        if len(recent) > 1:
            stats["std_dev_recent"] = round(statistics.stdev(recent), 3)
        
        if len(recent) >= 10:
            sorted_times = sorted(recent)
            stats["p50_latency"] = round(sorted_times[len(sorted_times) // 2], 3)
            stats["p95_latency"] = round(sorted_times[int(len(sorted_times) * 0.95)], 3)
            stats["p99_latency"] = round(sorted_times[int(len(sorted_times) * 0.99)], 3)
        
        return stats

    def get_summary_statistics(self) -> Dict[str, Any]:
        if not self.response_times:
            return {"error": "No latency data recorded"}
        
        stats = self._calculate_statistics()
        stats["average_latency_all"] = round(statistics.mean(self.response_times), 3)
        stats["median_latency_all"] = round(statistics.median(self.response_times), 3)
        
        # Distribution
        cats = {"excellent": 0, "good": 0, "acceptable": 0, "poor": 0}
        for t in self.response_times:
            c, _ = self._categorize_latency(t)
            cats[c] += 1
        
        stats["performance_distribution"] = {
            k: {"count": v, "percentage": round(v / len(self.response_times) * 100, 1)}
            for k, v in cats.items()
        }
        
        return stats

    def reset_statistics(self):
        self.response_times = []
        logger.info("Latency statistics reset")
