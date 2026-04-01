from typing import Any
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

class CostEstimator:
    """Estimates the financial cost of an execution"""
    
    @staticmethod
    @observe(name="estimate_cost")
    def estimate(specs: AgentExecutionSpec) -> float:
        """
        Estimate execution cost based on specs
        
        Args:
            specs: The agent execution specifications
            
        Returns:
            Estimated cost in USD
        """
        cost = 0.0
        
        try:
            if specs.provider:
                # Rough cost estimate based on tokens
                # Handle both object and dict access for flexibility
                if hasattr(specs.provider, 'max_tokens'):
                    max_tokens = specs.provider.max_tokens
                elif isinstance(specs.provider, dict):
                    max_tokens = specs.provider.get('max_tokens')
                else:
                    max_tokens = 2000
                
                estimated_tokens = max_tokens if max_tokens else 2000
                # Placeholder rate: $0.01 per 1K tokens
                cost += estimated_tokens * 0.00001
            
            # Add data source costs (e.g. vector DB read units)
            if specs.data_sources:
                cost += len(specs.data_sources) * 0.001
            
            # Add tool costs (e.g. API calls)
            if specs.tools:
                cost += len(specs.tools) * 0.005
            
            return round(cost, 4)
            
        except Exception as e:
            logger.warning(f"Cost estimation failed: {e}")
            return 0.0
