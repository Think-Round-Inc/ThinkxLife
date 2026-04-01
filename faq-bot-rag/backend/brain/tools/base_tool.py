"""
Base Tool - Abstract base class for all Brain tools
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result from tool execution"""
    tool_name: str
    success: bool
    content: Any
    metadata: Dict[str, Any]
    error: Optional[str] = None


class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self._initialized = False
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    async def initialize(self) -> bool:
        """Initialize the tool"""
        self._initialized = True
        return True
    
    def get_description(self) -> str:
        """Get tool description"""
        return self.__doc__ or f"{self.name} tool"
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get tool parameters schema"""
        return {}
    
    async def close(self) -> None:
        """Close tool and cleanup resources"""
        self._initialized = False

