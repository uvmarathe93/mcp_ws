from mcp_ws import MCPWebSocketServer, tool

app = MCPWebSocketServer("ExampleServer")

@tool
def add(a: int, b: int):
    """Add two numbers."""
    return a + b

if __name__ == "__main__":
    app.run(port=8765)
