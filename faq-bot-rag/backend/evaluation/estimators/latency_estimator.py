from typing import Dict, Any, Optional
import logging

# Try to import AgentExecutionSpec, but handle circular imports if necessary
try:
    from brain.specs import AgentExecutionSpec
except ImportError:
    # Fallback for type hinting if imported in a context where brain is not ready
    AgentExecutionSpec = Any

# Conditional Langfuse import (Langfuse 3.7.0+)
try:
    from langfuse import observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    # Create no-op decorator
    def observe(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)

class LatencyEstimator:
    """Estimates the latency (duration) of an execution"""
    
    @staticmethod
    @observe(name="estimate_latency")
    def estimate(specs: AgentExecutionSpec, history_stats: Optional[Dict[str, Any]] = None) -> float:
        """
        Estimate execution latency based on specs and historical performance
        
        Args:
            specs: The agent execution specifications
            history_stats: Optional statistics from LatencyEvaluator (e.g. average_latency_recent)
            
        Returns:
            Estimated latency in seconds
        """
        # 1. Determine baseline
        baseline = 0.5  # Default heuristic baseline
        
        # Use historical average if available and valid
        if history_stats and "average_latency_recent" in history_stats:
            avg = history_stats["average_latency_recent"]
            if isinstance(avg, (int, float)) and avg > 0:
                baseline = avg
                # If we are using history, we assume it mostly captures the "typical" complexity.
                # We will be conservative and still add some overhead for complex specs below,
                # but maybe weighted down.
        
        # 2. Calculate complexity overhead
        overhead = 0.0
        
        # Data sources add latency (IO)
        if specs.data_sources:
            overhead += len(specs.data_sources) * 0.3
        
        # Tools add latency (Network/Processing)
        if specs.tools:
            overhead += len(specs.tools) * 0.5
        
        # Provider latency
        # If we don't have history, we must guess the provider latency.
        # If we DO have history, the provider latency is likely built into the baseline average.
        if not history_stats and specs.provider:
            overhead += 1.5
            
        # If we have history, we treat the "overhead" as "additional complexity above average"
        # But since we don't know if this request is "above average", we might just add a fraction
        # or just use the baseline if specs look "standard".
        # For now, let's add the full overhead calculation to be safe/conservative.
        
        return round(baseline + overhead, 2)

