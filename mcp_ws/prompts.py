# mcp_ws/prompts.py
from typing import Dict, Optional
from mcp_ws.models.prompt import Prompt

class PromptRegistry:
    """
    Instance-based prompt registry for MCP.
    Supports dynamic registration and retrieval of prompts.
    """

    def __init__(self):
        self.prompts: Dict[str, Dict] = {}
        self.prompt_schemas: Dict[str, Dict] = {}

    # --------------------------
    # Registration
    # --------------------------
    def register(
        self,
        name: str,
        text: str,
        title: str = "",
        description: str = "",
        mimeType: str = "text/plain"
    ):
        """
        Register a prompt with metadata.
        """
        self.prompts[name] = {
            "name": name,
            "title": title,
            "description": description,
            "mimeType": mimeType,
            "text": text
        }

        self.prompt_schemas[name] = {
            "name": name,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "text": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "mimeType": {"type": "string"},
                },
                "required": ["name", "text"]
            }
        }
        return self.prompts[name]

    # --------------------------
    # Decorator for convenience
    # --------------------------
    def prompt(
        self,
        name: str,
        title: str = "",
        description: str = "",
        mimeType: str = "text/plain"
    ):
        """
        Decorator to register a prompt function returning text.
        Usage:
            @prompts.prompt("greeting")
            def greeting_prompt():
                return "Hello {name}!"
        """
        def decorator(func):
            text = func() if callable(func) else str(func)
            self.register(
                name=name,
                text=text,
                title=title,
                description=description,
                mimeType=mimeType
            )
            return func
        return decorator

    # --------------------------
    # Resolver
    # --------------------------
    def get(self, name: str) -> Optional[Dict]:
        """
        Get the prompt by name.
        """
        return self.prompts.get(name)
