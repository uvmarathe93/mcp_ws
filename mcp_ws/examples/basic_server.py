from mcp_ws import MCPWebSocketServer, tool

app = MCPWebSocketServer("ExampleServer")

@tool
def add(a: int, b: int):
    """Add two numbers."""
    print(f"Adding {a} and {b}")
    return a + b

# Register tool with your server instance
#app.register_tool(add)

# if __name__ == "__main__":
#     app.run(port=8765)
