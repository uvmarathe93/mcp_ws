from typing import Any, Optional
from pydantic import BaseModel


class JSONRPCMessage(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[Any] = None
    result: Optional[Any] = None
    error: Optional[Any] = None

    class Config:
        extra = "allow"


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


def rpc_result(req_id: str, result: Any) -> JSONRPCMessage:
    return JSONRPCMessage(id=req_id, result=result)


def rpc_error(req_id: str, code: int, message: str, data: Any = None) -> JSONRPCMessage:
    return JSONRPCMessage(
        id=req_id,
        error=JSONRPCError(code=code, message=message, data=data)
    )


def rpc_notification(method: str, params: Any = None) -> JSONRPCMessage:
    return JSONRPCMessage(
        method=method,
        params=params
    )
        