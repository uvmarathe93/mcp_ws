# examples/full_featured_server.py
import asyncio
from mcp_ws import MCPWebSocketServer, tool

app = MCPWebSocketServer("FullFeaturedExample")

# ---------------------------------------------------------
# 🔧 1. TOOLS
# ---------------------------------------------------------

@tool(app)
def add(a: int, b: int):
    """Add two numbers."""
    result = a + b

    # 🔥 Log to dashboard
    app.broadcast_log({
            "type": "log",
            "level": "info",
            "message": f"Tool add() called → {a} + {b} = {result}"
        }
    )

    return result


@tool(app)
async def slow_double(x: int):
    """Double a number after slow computation."""
    await asyncio.sleep(1)
    result = x * 2

    app.broadcast_log({
        "type": "log",
        "level": "debug",
        "message": f"slow_double finished computing {result}"
    })

    return result


# ---------------------------------------------------------
# 📦 2. RESOURCES (static or dynamic)
# ---------------------------------------------------------

# Example: static resource
def get_config():
    """Return server configuration details."""
    return {
        "version": "1.0.0",
        "env": "development",
        "features": ["tools", "resources", "prompts", "logs"]
    }
    
# Register resource with the server's ResourceRegistry
app.resources.register(
    name="config",
    get_text=get_config,
    title="Server Configuration",
    description="Server configuration details",
    mimeType="application/json"
)


# Example: dynamic resource
async def get_server_time():
    """Return current server time."""
    import datetime
    now = datetime.datetime.now().isoformat()

    app.broadcast_log({
        "type": "log",
        "level": "info",
        "message": f"Resource 'time' fetched at {now}"
    })

    return {"server_time": now}


app.resources.register(
    name="time",
    get_text=get_server_time,
    title="Server Time",
    description="Current server time",
    mimeType="application/json"
)


# ---------------------------------------------------------
# 💬 3. PROMPTS — Create / Update / Delete
# ---------------------------------------------------------
app.prompts.register(
    name="welcome",
    text="Welcome {user}!",
    description="Greeting prompt"
)


# ---------------------------------------------------------
# 📜 4. LOGGING (manual examples)
# ---------------------------------------------------------

@tool(app)
def test_log(message: str, level: str = "info"):
    """Send a manual log entry to dashboard."""
    
    app.broadcast_log({
            "type": "log",
            "level": level,
            "message": message
        }
    )
    return {"logged": True}


app.events.register(
    name="build_complete",
    description="Fired when build process completes."
)

app.events.register(
    name="ping",
    description="Simple heartbeat event."
)

# ---------------------------------------------------------
# 🚀 MCP Server Entry Point
# ---------------------------------------------------------
# if __name__ == "__main__":
#     app.run(port=8765)
