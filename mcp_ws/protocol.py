from .tool import TOOLS
import inspect

def get_tool_schema(func):
    sig = inspect.signature(func)
    props = {}

    for name, param in sig.parameters.items():
        ptype = param.annotation.__name__ if param.annotation != inspect._empty else "string"
        props[name] = {"type": ptype}

    return {
        "name": func.__name__,
        "description": func.__doc__ or "",
        "parameters": {"type": "object", "properties": props}
    }


def mcp_initialize(request_id):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True}
            },
            "serverInfo": {
                "name": "mcp_ws",
                "version": "0.1.0",
            }
        }
    }


def mcp_tools_list(request_id):
    tools = [get_tool_schema(func) for func in TOOLS.values()]
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": tools
        }
    }


def mcp_tools_call(request_id, params):
    name = params.get("name")
    args = params.get("arguments", {})

    if name not in TOOLS:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"message": f"Unknown tool: {name}"}
        }

    func = TOOLS[name]
    result = func(**args)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result
    }
