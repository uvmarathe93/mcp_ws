# mcp_ws/resources.py
from typing import Callable, Dict, Optional, List


class ResourceRegistry:
    """
    Instance-based resource registry for MCP server.
    Supports dynamic registration and retrieval of resources.
    """

    def __init__(self):
        self.resources: Dict[str, dict] = {}
        self.resource_schemas: Dict[str, dict] = {}

    # --------------------------
    # Registration
    # --------------------------
    def register(
        self,
        name: str,
        get_text: Callable,
        uri: Optional[str] = None,
        title: str = "",
        description: str = "",
        mimeType: str = "text/plain",
        icons: Optional[List[str]] = None
    ):
        uri = uri or f"resource://{name}"
        icons = icons or []

        self.resources[name] = {
            "name": name,
            "uri": uri,
            "title": title,
            "description": description,
            "mimeType": mimeType,
            "icons": icons,
            "get_text": get_text  # dynamic resolver
        }

        # Minimal schema; resources don't accept parameters
        self.resource_schemas[name] = {
            "name": name,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }

    # --------------------------
    # Decorator for convenience
    # --------------------------
    def resource(
        self,
        name: str,
        uri: Optional[str] = None,
        title: str = "",
        description: str = "",
        mimeType: str = "text/plain",
        icons: Optional[List[str]] = None
    ):
        """
        Decorator to register a function as a resource.
        Usage:
            @resources.resource("config")
            def config():
                return "hello"
        """
        def decorator(func):
            self.register(
                name=name,
                get_text=func,
                uri=uri,
                title=title,
                description=description,
                mimeType=mimeType,
                icons=icons
            )
            return func
        return decorator

    # --------------------------
    # Resolver
    # --------------------------
    def get_text(self, name: str):
        res = self.resources.get(name)
        if not res:
            return None
        return res["get_text"]()
