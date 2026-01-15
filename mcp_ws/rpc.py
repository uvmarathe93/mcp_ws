import json

def parse_jsonrpc(message: str):
    try:
        return json.loads(message)
    except Exception:
        return None

def make_result(id, result):
    return {
        "jsonrpc": "2.0",
        "id": id,
        "result": result
    }

def make_error(id, message):
    return {
        "jsonrpc": "2.0",
        "id": id,
        "error": {"message": message}
    }
