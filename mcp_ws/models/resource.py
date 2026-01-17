from typing import Any, Dict, Optional
from pydantic import BaseModel


class ResourceMetadata(BaseModel):
    mimeType: str = "text/plain"
    description: Optional[str] = None
    size: Optional[int] = None


class Resource(BaseModel):
    name: str
    path: str
    metadata: Optional[ResourceMetadata] = None


class ResourceContent(BaseModel):
    name: str
    content: Any     # could be str, bytes, JSON
    mimeType: str = "text/plain"
