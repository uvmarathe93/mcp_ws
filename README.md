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
