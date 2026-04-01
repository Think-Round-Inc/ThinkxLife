"""
Reasoning engine specifications and types
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field


# Reasoning-specific types can be added here as needed
# Currently reasoning engine uses other specs (ProviderSpec, ToolSpec, etc.)

@dataclass
class ReasoningContext:
    """Context for reasoning engine decisions"""
    request_message: str
    execution_history: List[str] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)
    available_data_sources: List[str] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)
    remaining_iterations: int = 3

