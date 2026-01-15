import asyncio
from .transport.websocket import run_websocket_server

class MCPWebSocketServer:
    def __init__(self, name="mcp_ws"):
        self.name = name

    def run(self, host="0.0.0.0", port=8765):
        print(f"MCP WebSocket server running at ws://{host}:{port}")
        asyncio.run(run_websocket_server(host, port))
