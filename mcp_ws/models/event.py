from typing import Any, Dict
from pydantic import BaseModel


class Event(BaseModel):
    name: str
    description: str


class EventPayload(BaseModel):
    event: str
    data: Dict[str, Any]
