TOOLS = {}

def tool(func):
    """
    Decorator to register a function as an MCP tool.
    """
    TOOLS[func.__name__] = func
    return func
