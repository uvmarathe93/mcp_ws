# mcp_ws/tool.py

from typing import Callable
from .models.tool import ToolParameter, ToolDefinition
from .protocol import get_tool_schema as protocol_get_tool_schema

def get_tool_schema(func: Callable):
    """
    Generate MCP-compliant schema from function annotations.
    """
    return protocol_get_tool_schema(func)


def tool(server):
    """
    Decorator to register a function as a tool on the given MCPWebSocketServer instance.

    Usage:
        @tool(server_instance)
        def add(a: int, b: int):
            return a + b
    """
    def decorator(func: Callable):
        # Initialize server registries if not present
        if not hasattr(server, "tools"):
            server.tools = {}
            server.tool_schemas = {}
            server.tool_subscribers = {}

        # Register the tool
        name = func.__name__
        server.tools[name] = func
        server.tool_schemas[name] = get_tool_schema(func)
        server.tool_subscribers.setdefault(name, set())

        return func

    return decorator