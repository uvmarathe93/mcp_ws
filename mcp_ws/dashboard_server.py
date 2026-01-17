import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path

# Serve the correct dashboard folder
DASHBOARD_DIR = Path(__file__).parent.resolve() / "dashboard"

def run_dashboard(port=8001, open_browser=True):
    handler_class = http.server.SimpleHTTPRequestHandler

    # Make a handler class that serves from DASHBOARD_DIR
    class Handler(handler_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    httpd = socketserver.TCPServer(("0.0.0.0", port), Handler)
    print(f"[MCP] Dashboard running at http://localhost:{port}")

    if open_browser:
        threading.Thread(target=lambda: webbrowser.open(f"http://localhost:{port}")).start()

    httpd.serve_forever()


if __name__ == "__main__":
    run_dashboard()