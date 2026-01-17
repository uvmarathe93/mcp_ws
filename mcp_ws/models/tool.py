from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ToolParameter(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None


class ToolDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: List[ToolParameter] = []
    returns: Optional[str] = None  # e.g. "integer", "string", "object"


class ToolCallResult(BaseModel):
    tool: str
    arguments: Dict[str, Any]
    result: Any
