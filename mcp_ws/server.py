# mcp_ws/server.py

import asyncio
import json
from typing import Set, Dict
import websockets

from .transport.websocket import run_websocket_server, broadcast_log
from .tool import get_tool_schema
#from .resources import RESOURCES, RESOURCE_SCHEMAS
from .resources import ResourceRegistry
from .prompts import PromptRegistry
from .events import EVENTS
from .protocol import (
    mcp_notify_tools_list_changed,
    mcp_notify_resources_list_changed,
    mcp_notify_prompts_list_changed,
)


class MCPWebSocketServer:
    def __init__(self, name: str = "mcp_ws", host: str = "0.0.0.0", port: int = 8765):
        self.name = name
        self.host = host
        self.port = port

        # --------------------------
        # Connected clients
        # --------------------------
        self.mcp_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.dashboards: Set[websockets.WebSocketServerProtocol] = set()

        # --------------------------
        # Client metadata
        # --------------------------
        self.client_info: Dict = {}
        self.client_capabilities: Dict = {}

        # --------------------------
        # Registries
        # --------------------------
        self.tools : dict = {}
        self.tool_schemas : dict = {}
        self.resources = ResourceRegistry()
        #self.resources = dict(RESOURCES)
        #self.resource_schemas = dict(RESOURCE_SCHEMAS)
        #self.prompts = dict(PROMPTS)
        self.prompts = PromptRegistry()
        self.events = dict(EVENTS)

        # --------------------------
        # Subscription registries
        # --------------------------
        self.tool_subscribers: Dict[str, Set[websockets.WebSocketServerProtocol]] = {name: set() for name in self.tools}
        self.prompt_subscribers: Dict[str, Set[websockets.WebSocketServerProtocol]] = {name: set() for name in self.prompts.prompts.keys()}
        self.resource_subscribers: Dict[str, Set[websockets.WebSocketServerProtocol]] = {name: set() for name in self.resources.resources.keys()}
        self.event_subscribers: Dict[str, Set[websockets.WebSocketServerProtocol]] = {name: set() for name in self.events}

    # ===============================================================
    # Server operation
    # ===============================================================
    def run(self):
        print(f"[MCP] WebSocket server running at ws://{self.host}:{self.port}")
        asyncio.run(run_websocket_server(self))

    def broadcast_log(self, message, level="info"):
        asyncio.create_task(broadcast_log(self, message, level))

    # ===============================================================
    # Notifications helpers
    # ===============================================================
    async def _send_notification(self, ws, notification):
        try:
            await ws.send(json.dumps(notification))
        except Exception:
            self.remove_client(ws)

    async def notify_all_clients(self, notification):
        for ws in list(self.mcp_clients | self.dashboards):
            await self._send_notification(ws, notification)

    async def notify_mcp_clients(self, notification):
        for ws in list(self.mcp_clients):
            await self._send_notification(ws, notification)

    async def notify_dashboards(self, notification):
        for ws in list(self.dashboards):
            await self._send_notification(ws, notification)

    # ===============================================================
    # Registry adders
    # ===============================================================
    def add_tool(self, name: str, func):
        """Register a new tool and notify clients."""
        self.tools[name] = func
        self.tool_schemas[name] = get_tool_schema(func)
        self.tool_subscribers.setdefault(name, set())
        asyncio.create_task(self.notify_all_clients(mcp_notify_tools_list_changed()))

    # def add_resource(self, name: str, resource_obj):
    #     self.resources[name] = resource_obj
    #     self.resource_subscribers.setdefault(name, set())
    #     asyncio.create_task(self.notify_all_clients(mcp_notify_resources_list_changed()))
    
    def add_resource(self, name: str, get_text_func, title="", description="", mimeType="text/plain", icons=None):
        self.resources.register(
            name=name,
            get_text=get_text_func,
            title=title,
            description=description,
            mimeType=mimeType,
            icons=icons
        )
        self.resource_subscribers.setdefault(name, set())
        asyncio.create_task(self.notify_all_clients(mcp_notify_resources_list_changed()))
    
    

    def add_prompt(self, name: str, prompt_obj):
        self.prompts[name] = prompt_obj
        self.prompt_subscribers.setdefault(name, set())
        asyncio.create_task(self.notify_all_clients(mcp_notify_prompts_list_changed()))

    def add_event(self, name: str, event_obj):
        self.events[name] = event_obj
        self.event_subscribers.setdefault(name, set())
        # Events notifications can be handled when emitted

    # ===============================================================
    # Client cleanup
    # ===============================================================
    def remove_client(self, ws):
        """Fully remove a client from all registries and subscriptions."""
        # Main sets
        self.mcp_clients.discard(ws)
        self.dashboards.discard(ws)

        # Subscriptions
        for subs in self.tool_subscribers.values():
            subs.discard(ws)
        for subs in self.prompt_subscribers.values():
            subs.discard(ws)
        for subs in self.resource_subscribers.values():
            subs.discard(ws)
        for subs in self.event_subscribers.values():
            subs.discard(ws)

        # Metadata
        self.client_info.pop(ws, None)
        self.client_capabilities.pop(ws, None)

        print(f"[MCP] Client removed cleanly: {ws}")
