from mcp_ws import MCPWebSocketServer, tool

app = MCPWebSocketServer("ExampleServer")

@tool
def add(a: int, b: int):
    """Add two numbers."""
    print(f"Adding {a} and {b}")
    return a + b

@tool
def multiply(a: int, b: int):
    """Multiply two numbers."""
    print(f"Multiplying {a} and {b}")
    return a * b

@tool
def subtract(a: int, b: int):
    """Subtract two numbers."""
    print(f"Subtracting {a} and {b}")
    return a - b

# =====================
# Tools
# =====================
@tool
def add(a: int, b: int):
    """Add two numbers."""
    print(f"[Tool] Adding {a} + {b}")
    return a + b

@tool
def multiply(a: int, b: int):
    """Multiply two numbers."""
    print(f"[Tool] Multiplying {a} * {b}")
    return a * b

# =====================
# Prompts
# =====================
# Example: store active prompts
active_prompts = []

@tool
def new_prompt(prompt_text: str):
    """Add a new prompt."""
    active_prompts.append(prompt_text)
    print(f"[Prompt] New prompt added: {prompt_text}")
    # Notify dashboards of updated prompts
    app.broadcast_log({"type": "prompts/update", "prompts": active_prompts})
    return {"status": "ok", "prompt": prompt_text}

# =====================
# Resources
# =====================
# Example: simple resource registry
resources = {}

@tool
def update_resource(name: str, value: str):
    """Update a named resource."""
    resources[name] = value
    print(f"[Resource] {name} = {value}")
    # Notify dashboards of updated resources
    app.broadcast_log({"type": "resources/update", "resources": resources})
    return {"status": "ok", "name": name, "value": value}

# =====================
# Logs
# =====================
# Logs are automatically sent to dashboards via websocket server
# Any print() in tools or broadcasts can be picked up by dashboards

# Register tool with your server instance
#app.register_tool(add)

# if __name__ == "__main__":
#     app.run(port=8765)
