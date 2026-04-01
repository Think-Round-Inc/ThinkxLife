"""
Tool specifications and types
"""

from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class ToolSpec:
    """Specification for a tool that agents want to use"""
    name: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    required_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "config": self.config,
            "required_params": self.required_params
        }

