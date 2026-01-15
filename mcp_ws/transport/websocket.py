import asyncio
import websockets
import json
from ..rpc import parse_jsonrpc
from ..protocol import (
    mcp_initialize,
    mcp_tools_list,
    mcp_tools_call
)

async def websocket_handler(websocket):
    async for message in websocket:
        request = parse_jsonrpc(message)
        if not request:
            continue

        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        if method == "initialize":
            response = mcp_initialize(req_id)

        elif method == "tools/list":
            response = mcp_tools_list(req_id)

        elif method == "tools/call":
            response = mcp_tools_call(req_id, params)

        else:
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"message": f"Unknown method: {method}"}
            }

        await websocket.send(json.dumps(response))


async def run_websocket_server(host, port):
    async with websockets.serve(websocket_handler, host, port):
        await asyncio.Future()
