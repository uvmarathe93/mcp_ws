# mcp_ws/events.py
from typing import Dict, Optional
from mcp_ws.models.event import Event


class EventRegistry:
    """
    Instance-based event registry, similar to Tools, Resources, Prompts.
    Stores the event name + description.
    """

    def __init__(self):
        self.events: Dict[str, Dict] = {}

    # --------------------------
    # Register
    # --------------------------
    def register(self, name: str, description: str = ""):
        self.events[name] = {
            "name": name,
            "description": description or ""
        }

    # --------------------------
    # Decorator (optional)
    # --------------------------
    def event(self, name: str, description: str = ""):
        """
        @app.events.event("my-event", "Some event")
        def handler(): ...
        """
        def decorator(func):
            self.register(name, description)
            return func
        return decorator

    # --------------------------
    # Retrieve
    # --------------------------
    def get(self, name: str) -> Optional[Dict]:
        return self.events.get(name)

    def list(self):
        return self.events
