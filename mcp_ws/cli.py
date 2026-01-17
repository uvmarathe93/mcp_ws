import argparse
import os
import sys
import time
import subprocess
from pathlib import Path
import importlib
import threading
from mcp_ws.dev import run_with_reload
from mcp_ws.dashboard_server import run_dashboard


BASE_DIR = Path(__file__).resolve().parent


def run_server_with_reload(cmd_args):
    """
    Run the server as a subprocess with automatic reload on .py file changes.
    """
    last_mtime = None
    process = None

    watch_dirs = [BASE_DIR]

    while True:
        # compute combined mtimes
        mtimes = []
        for d in watch_dirs:
            for root, _, files in os.walk(d):
                for f in files:
                    if f.endswith(".py"):
                        mtimes.append(os.path.getmtime(os.path.join(root, f)))
        new_mtime = hash(tuple(mtimes))

        if last_mtime is None or new_mtime != last_mtime:
            last_mtime = new_mtime
            if process:
                print("[MCP] 🔁 Restarting server...")
                process.terminate()
                process.wait()

            process = subprocess.Popen([sys.executable] + cmd_args)
        time.sleep(1)


def serve_mcp(app_target: str = None, reload: bool = False):
    """
    Serve the MCP server.

    - If app_target is None, run default server.py
    - If app_target is module:attribute, run user server instance
    """
    print("In serve MCP")
    if ":" not in app_target:
        print("[MCP] ERROR: app must be in format module:attribute, e.g. my_server:server")
        sys.exit(1)

    print(app_target)
    module_name, attr_name = app_target.split(":")
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        print(f"[MCP] ERROR: Cannot import module '{module_name}': {exc}")
        sys.exit(1)

    server = getattr(module, attr_name, None)
    if server is None:
        print(f"[MCP] ERROR: Module '{module_name}' has no attribute '{attr_name}'")
        sys.exit(1)

    if reload:
        # Hot reload for the server
        run_server_with_reload(["-m", "mcp_ws.cli", "serve", app_target])
    else:
        server.run()


def serve_dashboard(reload_enabled=False):
    from .dashboard_server import run_dashboard
    if reload_enabled:
        run_server_with_reload(["-m", "mcp_ws.cli", "dashboard"])
    else:
        run_dashboard(port=8001, open_browser=True)


def run_all(app_target: str, reload: bool):
    """
    Run user MCP server given as module:attribute
    """
    print("In run all")
    if ":" not in app_target:
        print("[MCP] ERROR: app must be in format module:attribute, e.g. my_server:server")
        sys.exit(1)

    module_name, attr_name = app_target.split(":")
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        print(f"[MCP] ERROR: Cannot import module '{module_name}': {exc}")
        sys.exit(1)

    server = getattr(module, attr_name, None)
    if server is None:
        print(f"[MCP] ERROR: Module '{module_name}' has no attribute '{attr_name}'")
        sys.exit(1)

    # Start dashboard in separate thread
    dashboard_thread = threading.Thread(
        target=lambda: run_dashboard(port=8001, open_browser=True),
        daemon=True
    )
    dashboard_thread.start()

    if reload:
        # Hot reload for the server
        run_server_with_reload(["-m", "mcp_ws.cli", "serve", app_target])
    else:
        server.run()


def main():
    print("[MCP] MCP WebSocket Server CLI")
    parser = argparse.ArgumentParser(description="MCP WS CLI")
    sub = parser.add_subparsers(dest="command")

    srv = sub.add_parser("serve", help="Start MCP WebSocket server")
    srv.add_argument("app", 
        help="User MCP server instance in module:attribute format, e.g. my_server:server"
    )
    srv.add_argument("--reload", action="store_true")

    dash = sub.add_parser("dashboard", help="Start Dashboard server")
    dash.add_argument("--reload", action="store_true")

    run_cmd = sub.add_parser("run", help="Start both MCP server + Dashboard")
    run_cmd.add_argument("app", 
        help="User MCP server instance in module:attribute format, e.g. my_server:server"
    )
    run_cmd.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    if args.command == "serve":
        serve_mcp(args.app, args.reload)
    elif args.command == "dashboard":
        serve_dashboard(args.reload)
    elif args.command == "run":
        run_all(args.app, args.reload)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
