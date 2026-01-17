# mcp_ws/protocol.py

import inspect
import asyncio
import json
from typing import Dict, Any

from mcp_ws.models.tool import ToolDefinition, ToolParameter
from mcp_ws.models.resource import Resource, ResourceMetadata, ResourceContent
from mcp_ws.models.prompt import Prompt, PromptValue
from mcp_ws.models.event import Event, EventPayload

# --------------------------
# Helpers
# --------------------------
def map_python_type(t):
    if t in [int]:
        return "integer"
    if t in [float]:
        return "number"
    if t in [bool]:
        return "boolean"
    return "string"


def get_tool_schema(func):
    """Convert a Python function into MCP-compliant tool schema using ToolDefinition"""
    sig = inspect.signature(func)
    parameters = []
    required = []

    for name, param in sig.parameters.items():
        ptype = map_python_type(param.annotation) if param.annotation != inspect._empty else "string"
        is_required = param.default == inspect._empty
        parameters.append(
            ToolParameter(
                name=name,
                type=ptype,
                required=is_required,
                default=None if is_required else param.default
            )
        )
        if is_required:
            required.append(name)

    tool_def = ToolDefinition(
        name=func.__name__,
        description=func.__doc__ or "",
        parameters=parameters
    )

    return {
        "name": tool_def.name,
        "description": tool_def.description,
        "inputSchema": {
            "type": "object",
            "properties": {p.name: {"type": p.type} for p in tool_def.parameters},
            "required": required
        }
    }

# --------------------------
# MCP Core
# --------------------------
def mcp_initialize(request_id: str):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": False},
                "prompts": {"listChanged": True},
                "events": {"subscribe": True},
                "logging": {"supports": ["stderr", "stdout"]}
            },
            "serverInfo": {"name": "mcp_ws", "version": "0.2.0"}
        }
    }


# --------------------------
# Tools API
# --------------------------
def mcp_tools_list(request_id: str, TOOLS: Dict[str, Any]):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"tools": [get_tool_schema(f) for f in TOOLS.values()]}
    }


def mcp_tools_call(request_id: str, params: Dict[str, Any], TOOLS: Dict[str, Any], TOOL_SCHEMAS: Dict[str, Any]):
    name = params.get("name")
    args = params.get("arguments", {})

    if name not in TOOLS:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Unknown tool: {name}"}
        }

    schema = TOOL_SCHEMAS[name]["inputSchema"]
    parsed_args = {}
    errors = []

    for key in schema.get("required", []):
        if key not in args:
            errors.append(f"Missing required parameter: {key}")

    for key, val in args.items():
        expected_type = schema["properties"][key]["type"]
        try:
            if expected_type == "integer":
                parsed_args[key] = int(val)
            elif expected_type == "number":
                parsed_args[key] = float(val)
            elif expected_type == "boolean":
                parsed_args[key] = val if isinstance(val, bool) else str(val).lower() == "true"
            else:
                parsed_args[key] = str(val)
        except Exception:
            errors.append(f"Invalid type for parameter '{key}': expected {expected_type}")

    if errors:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32602, "message": "; ".join(errors)}
        }

    result = TOOLS[name](**parsed_args)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result if isinstance(result, dict) else {"result": result}
    }



# --------------------------
# Resources API
# --------------------------
async def mcp_resources_list(req_id: str, resources_registry) -> Dict[str, Any]:
    """
    List all resources with resolved text content.
    resources_registry: instance of ResourceRegistry
    """
    items = []

    for name, res in resources_registry.resources.items():
        text_field = res["get_text"]

        # Resolve the text (supports async functions)
        if callable(text_field):
            val = text_field()
            val = await val if asyncio.iscoroutine(val) else val
            text_value = val if isinstance(val, str) else json.dumps(val, indent=2)
        else:
            text_value = str(text_field)

        resource = Resource(
            name=name,
            path=res["uri"],
            metadata=ResourceMetadata(
                mimeType=res["mimeType"],
                description=res["description"]
            )
        )

        content = ResourceContent(
            name=name,
            content=text_value,
            mimeType=res["mimeType"]
        )

        items.append({
            "name": resource.name,
            "uri": resource.path,
            "title": res["title"],
            "description": resource.metadata.description,
            "mimeType": resource.metadata.mimeType,
            "icons": res["icons"],
            "text": content.content
        })

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {"resources": items}
    }


def mcp_resources_read(request_id: str, params: Dict[str, Any], resources_registry) -> Dict[str, Any]:
    """
    Read a single resource by URI.
    resources_registry: instance of ResourceRegistry
    """
    uri = params.get("uri")

    for res in resources_registry.resources.values():
        if res["uri"] == uri:
            # Resolve text dynamically
            text_field = res["get_text"]
            text_value = text_field() if not asyncio.iscoroutinefunction(text_field) else asyncio.run(text_field())
            text_value = text_value if isinstance(text_value, str) else json.dumps(text_value, indent=2)

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {**res, "text": text_value}
            }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32000, "message": "Resource not found"}
    }


# --------------------------
# Prompts API (refactored for PromptRegistry)
# --------------------------
def mcp_prompts_list(request_id: str, prompt_registry):
    """
    Returns the list of all prompts registered in the server.
    prompt_registry: instance of PromptRegistry
    """
    prompt_list = []
    for name, data in prompt_registry.prompts.items():
        p = Prompt(
            name=name,
            description=data.get("description", ""),
            variables=data.get("variables", {}),
            template=data.get("text", "")
        )
        prompt_list.append(p.dict())

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": prompt_list
    }


def mcp_prompts_read(request_id: str, params: dict, prompt_registry):
    """
    Returns a single prompt by name.
    """
    name = params.get("name")
    data = prompt_registry.get(name)
    if not data:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": f"Prompt '{name}' not found"}
        }

    p = Prompt(
        name=name,
        description=data.get("description", ""),
        variables=data.get("variables", {}),
        template=data.get("text", "")
    )

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": p.dict()
    }


# --------------------------
# Events API (refactored)
# --------------------------
def mcp_events_list(request_id: str, event_registry):
    items = []

    for name, data in event_registry.events.items():
        e = Event(
            name=name,
            description=data.get("description", "")
        )
        items.append(e.dict())

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": items
    }


# --------------------------
# Notifications
# --------------------------
def mcp_initialized_notification():
    return {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}

def mcp_notify_resources_list_changed():
    return {"jsonrpc": "2.0", "method": "notifications/resources/list_changed", "params": {}}

def mcp_notify_tools_list_changed():
    return {"jsonrpc": "2.0", "method": "notifications/tools/list_changed", "params": {}}

def mcp_notify_prompts_list_changed():
    return {"jsonrpc": "2.0", "method": "notifications/prompts/list_changed", "params": {}}

# --------------------------
# Ping / Health
# --------------------------
def mcp_ping(request_id: str):
    return {"jsonrpc": "2.0", "id": request_id, "result": {}}
