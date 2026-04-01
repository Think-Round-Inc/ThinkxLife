"""
Brain Tools - Tool implementations for workflow engine
Compatible with LangGraph-based orchestration
"""

__all__ = []

# Core classes
from .base_tool import BaseTool, ToolResult
from .tool_registry import ToolRegistry, get_tool_registry

__all__.extend(["BaseTool", "ToolResult", "ToolRegistry", "get_tool_registry"])

# Tools
try:
    from .tavily_search import TavilySearchTool, create_tavily_search_tool
    __all__.extend(["TavilySearchTool", "create_tavily_search_tool"])
except ImportError as e:
    print(f"Warning: Tavily Search Tool not available: {e}")



# Factory function to create tools
def create_tool(tool_type: str, config: dict = None):
    """Factory function to create tools with default settings"""
    if config is None:
        config = {}
    
    tool_map = {
        "tavily_search": (TavilySearchTool, create_tavily_search_tool),
    }
    
    if tool_type not in tool_map:
        raise ValueError(f"Unknown tool type: {tool_type}. Available: {list(tool_map.keys())}")
    
    tool_class, factory_func = tool_map[tool_type]
    
    if tool_class.__name__ not in __all__:
        raise ImportError(f"{tool_type} tool not available. Check dependencies.")
    
    return factory_func(config)


# Get available tools
def get_available_tools():
    """Get list of available tool types"""
    available = []
    tool_map = {
        "TavilySearchTool": "tavily_search",
    }
    
    for class_name, tool_type in tool_map.items():
        if class_name in __all__:
            available.append(tool_type)
    
    return available


def get_tool_config_template(tool_type: str) -> dict:
    """Get default configuration template for a tool"""
    try:
        tool = create_tool(tool_type, {})
        if hasattr(tool, 'get_default_config'):
            return tool.get_default_config()
        return {}
    except Exception as e:
        raise ValueError(f"Could not get config for {tool_type}: {str(e)}")

