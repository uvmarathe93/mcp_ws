# mcp_ws — Minimal WebSocket-based MCP Server Framework

`mcp_ws` is a lightweight, pure-Python framework for creating **Model Context Protocol (MCP)** servers over **WebSockets**.  
It provides a clean JSON-RPC 2.0 transport, automatic tool discovery, schema generation, method dispatching, and complete MCP-compatible initialization flows.

This project is ideal if you want to:

- Build a **custom local MCP server**
- Expose your own **tools**, **resources**, or **prompts** over WebSockets
- Integrate with MCP-compatible clients (e.g., AI agent runners)
- Embed tools into an LLM workflow with low overhead
- Learn how MCP works internally

---

## 🚀 Features

- **Pure WebSocket MCP server** (no FastAPI, no HTTP)
- **JSON-RPC 2.0 compliant**
- `initialize` handshake fully implemented
- Automatic **tool registry**
- Automatic **tool parameter schema**
- Clean `@tool` decorator for writing tools
- Extensible transport layer
- Support for MCP messages:
  - `initialize`
  - `tools/list`
  - `tools/call`
  - notifications passthrough
- Simple architecture, easy to extend
- Works on **Python 3.10+**

---

## 📦 Installation (Local Development)

Clone and install in editable mode:

```bash
git clone https://github.com/uvmarathe93/mcp_ws.git
cd mcp_ws
pip install -e .
```

## 🧪 Quick Start — Your First MCP Server
Create server.py
```python
from mcp_ws import MCPWebSocketServer, tool

server = MCPWebSocketServer()

@tool
def add(a: int, b: int):
    """Add two numbers."""
    return {"result": a + b}

server.start("0.0.0.0", 8765)
```

Run:
```bash
python server.py
```
Your MCP server is now live at:
```bash
ws://localhost:8765
```

## 🧩 Testing the Server (HTML Client Included)
Open MCPTest.html in your browser.

Enter:
```bash
ws://localhost:8765
```

Click Connect → sends initialize.

Test:
- initialize
- tools/list
- tools/call
- Custom JSON-RPC messages

This HTML file is tailored to MCP and will display raw incoming/outgoing messages.

## 🛠️ How Tools Work
Define a tool using the @tool decorator:
```python
@tool
def greet(name: str):
    """Say hello to someone."""
    return {"message": f"Hello, {name}!"}
```

- ✔ Automatic tool registration
- ✔ Automatic JSON schema generation
- ✔ Included in tools/list
- ✔ Invocable via tools/call

## 📄 Example MCP Flow
1️⃣ initialize
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize"
}
```

Server → client:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": { "tools": { "listChanged": true } },
    "serverInfo": { "name": "mcp_ws", "version": "0.1.0" }
  }
}
```

2️⃣ tools/list
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": { "a": 5, "b": 6 }
  }
}
```

Response
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "result": 11
  }
}
```

## 📁 Project Structure
```bash
mcp_ws/
├── mcp_ws/
│   ├── protocol.py         # MCP protocol constants & versioning
│   ├── rpc.py              # JSON-RPC utilities
│   ├── server.py           # Core MCP WebSocket server
│   ├── tool.py             # Tool decorator + schema generator
│   ├── transport/
│   │   ├── websocket.py    # WebSocket transport implementation
│   ├── utils/
│   │   ├── json_utils.py
│   ├── examples/
│       └── basic_server.py
│
├── MCPTest.html            # Test client for browsers
├── pyproject.toml
└── README.md
```

## ⚙️ Architecture Overview
✔ Transport Layer

Abstracted; currently includes:

- WebSocket transport (transport/websocket.py)

Easily extended for:

- TCP sockets

- HTTP

- Named pipes

- Custom transports

✔ Protocol Layer

Defines:

- Capability negotiation

- Server info

- Standard MCP message structure

✔ RPC Layer

Handles:

- JSON-RPC parsing

- Envelope creation

- Error handling

✔ Tool System

Includes:

- Registry

- Schema generation

- Dispatching

- Type-safe argument parsing


## 📘 Tool Schema Generation
Given
```python
@tool
def multiply(a: int, b: int):
    """Multiply two numbers."""
    return a * b
```

It produces MCP schema
```json
{
  "name": "multiply",
  "description": "Multiply two numbers.",
  "parameters": {
    "type": "object",
    "properties": {
      "a": {"type": "integer"},
      "b": {"type": "integer"}
    },
    "required": ["a", "b"]
  }
}
```
This schema is returned in tools/list.

## 🔌 WebSocket Server API
Start Server
```python
server = MCPWebSocketServer()
server.start("0.0.0.0", 8765)
```

Start with asyncio
```python
await server.serve_async(host="0.0.0.0", port=8765)
```

Register tools programmatically
```python
server.register_tool(my_func)
```

## 🧪 Example Server (Included in Repo)
mcp_ws/examples/basic_server.py
```python
from mcp_ws import MCPWebSocketServer, tool

server = MCPWebSocketServer()

@tool
def ping():
    return {"message": "pong"}

server.start("0.0.0.0", 8765)
```

## 🚧 Roadmap
✓ Phase 1 (Complete)

- WebSocket MCP server

- Tool registry

- tools/list

- tools/call

- initialize handshake

- JSON schema generation

- HTML test client

🔜 Phase 2 (In progress)

- Streaming tool results

- Resource subscriptions

- Logging notifications

- Prompt registry

- Rich error codes

🔮 Phase 3 (Future)

- MCP client SDK in Python

- HTTP transport

- Named pipe transport

- Browser client package

- Publish to PyPI (mcp-ws)

## 🤝 Contributing

Contributions welcome!
Open an issue or PR — especially if you're building tools, adding transports, or extending MCP features.

## 📄 License
MIT License
