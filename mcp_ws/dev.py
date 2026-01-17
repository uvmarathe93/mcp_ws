# mcp_ws/dev.py

import time
import subprocess
import sys
import os
from pathlib import Path

WATCH_EXTENSIONS = {".py"}


def run_with_reload(module_path: str):
    print(f"[mcpws] Running with reload: {module_path}")

    # Track modification times
    mtimes = {}

    # Start initial server
    proc = start_subprocess(module_path)

    try:
        while True:
            changed = file_changed(mtimes)

            if changed:
                print(f"[mcpws] Detected change in: {changed}")
                print("[mcpws] Restarting server...")

                proc.kill()
                proc = start_subprocess(module_path)

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("[mcpws] Shutting down...")
        proc.kill()


def start_subprocess(module_path: str):
    return subprocess.Popen([sys.executable, "-m", module_path])


def file_changed(mtimes: dict):
    """
    Return changed file path or None.
    """
    for root, dirs, files in os.walk(Path.cwd()):
        for name in files:
            path = Path(root) / name

            if path.suffix not in WATCH_EXTENSIONS:
                continue

            try:
                mtime = path.stat().st_mtime
            except FileNotFoundError:
                continue

            old = mtimes.get(path)

            if old is None:
                mtimes[path] = mtime
            elif mtime != old:
                mtimes[path] = mtime
                return str(path)

    return None
