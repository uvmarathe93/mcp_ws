# mcp_ws/logging_api.py

def server_log(level: str, message: str):
    """
    Internal helper for server logging.
    MCP client will receive these as notifications.
    """
    print(f"[{level.upper()}] {message}")
