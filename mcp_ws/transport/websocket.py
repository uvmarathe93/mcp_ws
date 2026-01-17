# mcp_ws/transport/websocket.py

import asyncio
import json
import websockets
from ..protocol import (
    mcp_initialize,
    mcp_initialized_notification,
    mcp_ping,
    mcp_tools_list,
    mcp_tools_call,
    mcp_resources_list,
    mcp_resources_read,
    mcp_prompts_list,
    mcp_prompts_read,
    mcp_events_list,
)


# --------------------------
# Logging helper
# --------------------------
async def send_log(ws, message, level="info"):
    try:
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "logging/logMessage",
            "params": {"level": level, "message": message}
        }))
    except Exception:
        pass


async def broadcast_log(server, message, level="info"):
    for ws in list(server.dashboards):
        await send_log(ws, message, level)


# --------------------------
# JSON-RPC helper
# --------------------------
def parse_jsonrpc(message):
    try:
        return json.loads(message)
    except Exception:
        return None


# --------------------------
# Main WebSocket handler
# --------------------------
async def websocket_handler(ws, path, server):
    client_type = None
    try:
        async for message in ws:
            request = parse_jsonrpc(message)
            if not request:
                continue

            method = request.get("method")
            params = request.get("params", {})
            req_id = request.get("id")

            # --------------------------
            # Initialize client
            # --------------------------
            if method == "initialize":
                client_type = params.get("clientType", "mcp")
                if client_type == "dashboard":
                    server.dashboards.add(ws)
                    print(f"[MCP] Dashboard connected: {ws.remote_address}")
                else:
                    server.mcp_clients.add(ws)
                    print(f"[MCP] Client connected: {ws.remote_address}")

                await ws.send(json.dumps(mcp_initialize(req_id)))
                await ws.send(json.dumps(mcp_initialized_notification()))
                continue

            # --------------------------
            # Ping
            # --------------------------
            if method == "ping":
                await ws.send(json.dumps(mcp_ping(req_id)))
                continue

            # --------------------------
            # Tools
            # --------------------------
            if method == "tools/list":
                await ws.send(json.dumps(mcp_tools_list(req_id, server.tools)))
            elif method == "tools/call":
                await ws.send(json.dumps(mcp_tools_call(req_id, params, server.tools, server.tool_schemas)))
                continue

            # --------------------------
            # Resources
            # --------------------------
            if method == "resources/list":
                response = await mcp_resources_list(req_id, server.resources)
                await ws.send(json.dumps(response))
            elif method == "resources/read":
                await ws.send(json.dumps(mcp_resources_read(req_id, params, server.resources)))
                continue

            # --------------------------
            # Prompts
            # --------------------------
            if method == "prompts/list":
                await ws.send(json.dumps(mcp_prompts_list(req_id, server.prompts)))
            elif method == "prompts/read":
                await ws.send(json.dumps(mcp_prompts_read(req_id, params, server.prompts)))
                continue

            # --------------------------
            # Events
            # --------------------------
            if method == "events/list":
                await ws.send(json.dumps(mcp_events_list(req_id, server.events)))
                continue

            # --------------------------
            # Unknown method
            # --------------------------
            await ws.send(json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            }))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if client_type:
            server.remove_client(ws)
            print(f"[MCP] Client disconnected: {ws.remote_address}")


# --------------------------
# Run server
# --------------------------
async def run_websocket_server(server, host=None, port=None):
    host = host or server.host
    port = port or server.port
    print(f"[MCP] WebSocket server running @ ws://{host}:{port}")
    async with websockets.serve(lambda ws, path: websocket_handler(ws, path, server), host, port):
        await asyncio.Future()  # run forever
