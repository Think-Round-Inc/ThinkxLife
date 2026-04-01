"""
Tool Registry - Checks if tool files are available
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# Available tools list
TOOLS = ["tavily_search"]


class ToolRegistry:
    """
    Registry for tools
    
    Checks if tool files exist
    """
    
    def check_tool_available(self, tool_name: str) -> bool:
        """
        Check if tool file exists
        
        Checks if the tool_name exists in TOOLS list and if the
        corresponding .py file exists in the tools directory.
        
        Args:
            tool_name: Name of the tool (e.g., "tavily_search")
            
        Returns:
            True if tool is in TOOLS and file exists, False otherwise
        """
        # Check if tool is in TOOLS list
        if tool_name not in TOOLS:
            logger.warning(f"Tool '{tool_name}' not found in TOOLS list")
            return False
        
        # Check if .py file exists
        file_path = Path(__file__).parent / f"{tool_name}.py"
        exists = file_path.exists()
        
        if not exists:
            logger.warning(f"Tool file not found: {tool_name}.py")
        
        return exists


# Singleton
_tool_registry_instance = None


def get_tool_registry() -> ToolRegistry:
    """Get singleton ToolRegistry instance"""
    global _tool_registry_instance
    if _tool_registry_instance is None:
        _tool_registry_instance = ToolRegistry()
    return _tool_registry_instance
