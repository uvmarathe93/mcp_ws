from typing import Any, Dict, Optional
from pydantic import BaseModel


class Prompt(BaseModel):
    name: str
    description: Optional[str] = None
    variables: Dict[str, str] = {}   # var_name → description
    template: str = ""               # actual prompt text


class PromptValue(BaseModel):
    name: str
    variables: Dict[str, Any]
