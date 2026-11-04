#!/usr/bin/env python3
"""
Psytrance Night Outreach Agent — Desktop System Tray Companion.

Provides a desktop tray icon with menu actions to monitor status,
open the dashboard, trigger pipeline discovery, fetch replies, run repository sync,
and gracefully quit running application servers.

Falls back gracefully to a headless CLI / daemon interface in environments where
graphical desktop libraries (pystray, tkinter, PIL, or DISPLAY) are unavailable.
"""

import sys
import os
import time
import argparse
import webbrowser
import requests
import subprocess
import signal

DASHBOARD_URL = "http://localhost:5000"

def check_server_status(url=DASHBOARD_URL):
    """Check if the dashboard server is responding."""
    try:
        res = requests.get(url, timeout=2.0)
        return res.status_code == 200
    except Exception:
        return False

def open_dashboard():
    """Launch the dashboard in the default web browser."""
    print(f"[Tray] Opening dashboard at {DASHBOARD_URL}...")
    webbrowser.open(DASHBOARD_URL)

def run_pipeline():
    """Trigger the autonomous outreach pipeline immediately."""
    print("[Tray] Requesting manual pipeline run...")
    try:
        res = requests.post(f"{DASHBOARD_URL}/run_pipeline_now", timeout=5.0)
        data = res.json()
        print(f"[Tray] Pipeline response: {data.get('message', 'Triggered')}")
    except Exception as e:
        print(f"[Tray] Failed to trigger pipeline: {e}")

def fetch_replies():
    """Poll IMAP and Instagram inboxes for new incoming replies."""
    print("[Tray] Requesting reply inbox fetch...")
    try:
        res = requests.post(f"{DASHBOARD_URL}/fetch_replies", timeout=10.0)
        data = res.json()
        print(f"[Tray] Fetch response: {data.get('message', 'Checked')}")
    except Exception as e:
        print(f"[Tray] Failed to fetch replies: {e}")

def run_sync():
    """Execute repository synchronization protocol."""
    print("[Tray] Requesting repository sync protocol...")
    try:
        res = requests.post(f"{DASHBOARD_URL}/run_sync", timeout=30.0)
        data = res.json()
        print(f"[Tray] Sync status: {data.get('status')} | Output: {data.get('output', '')[:100]}...")
    except Exception as e:
        print(f"[Tray] Failed to execute sync: {e}")

def quit_servers(icon=None):
    """Gracefully terminate Flask server, background scheduler, and tray icon."""
    print("[Tray] Gracefully shutting down application server and tray companion...")
    try:
        requests.post(f"{DASHBOARD_URL}/shutdown", timeout=3.0)
    except Exception:
        pass

    if icon:
        try:
            icon.stop()
        except Exception:
            pass
    sys.exit(0)

def create_tray_image():
    """Generate a clean 64x64 PIL image icon for the system tray if PIL is installed."""
    try:
        from PIL import Image, ImageDraw
        image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((4, 4, 60, 60), fill=(26, 31, 38), outline=(88, 166, 255), width=3)
        draw.ellipse((16, 16, 48, 48), fill=(210, 153, 34), outline=(63, 185, 80), width=2)
        draw.ellipse((26, 26, 38, 38), fill=(88, 166, 255))
        return image
    except ImportError:
        return None

def run_gui_tray():
    """Attempt to initialize pystray system tray."""
    try:
        import pystray
        from PIL import Image
    except ImportError:
        print("[Tray] pystray or PIL not available. Falling back to CLI mode.")
        return False

    if not os.environ.get('DISPLAY') and sys.platform.startswith('linux'):
        print("[Tray] No graphical display detected ($DISPLAY empty). Running in headless CLI mode.")
        return False

    image = create_tray_image()
    if not image:
        return False

    menu = pystray.Menu(
        pystray.MenuItem("Psytrance Outreach Agent", lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Open Dashboard", lambda icon, item: open_dashboard()),
        pystray.MenuItem("Run Pipeline Now", lambda icon, item: run_pipeline()),
        pystray.MenuItem("Fetch Replies", lambda icon, item: fetch_replies()),
        pystray.MenuItem("Run Sync Protocol", lambda icon, item: run_sync()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit Servers & Exit", lambda icon, item: quit_servers(icon))
    )

    icon = pystray.Icon("psytrance_agent", image, "Psytrance Night Outreach Agent", menu)
    print("[Tray] Graphical System Tray initialized successfully.")
    icon.run()
    return True

def handle_single_command(cmd):
    """Handle a single CLI command string."""
    cmd = cmd.strip().lower()
    if cmd in ['1', 'open', 'dashboard']:
        open_dashboard()
    elif cmd in ['2', 'run', 'pipeline']:
        run_pipeline()
    elif cmd in ['3', 'fetch', 'replies']:
        fetch_replies()
    elif cmd in ['4', 'sync']:
        run_sync()
    elif cmd in ['5', 'status']:
        status = "ONLINE" if check_server_status() else "OFFLINE"
        print(f"[Tray] Dashboard status: {status}")
    elif cmd in ['q', 'quit', 'exit']:
        quit_servers()
    elif cmd == '':
        return
    else:
        print(f"Unknown command: '{cmd}'. Enter 1-5 or 'q'.")

def run_cli_daemon():
    """CLI companion mode when running in terminal or non-graphical environments."""
    print("=" * 60)
    print(" Psytrance Night Outreach Agent — Desktop Companion")
    print(f" Target Dashboard: {DASHBOARD_URL}")
    print("=" * 60)
    print("Commands:")
    print("  [1] Open Dashboard")
    print("  [2] Run Pipeline Now")
    print("  [3] Fetch Replies")
    print("  [4] Run Sync Protocol")
    print("  [5] Check Server Status")
    print("  [q] Quit Server & Exit")
    print("=" * 60)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        handle_single_command(line)

def main():
    parser = argparse.ArgumentParser(description="Psytrance Outreach System Tray Companion")
    parser.add_argument("--cli", action="store_true", help="Force CLI companion daemon mode")
    parser.add_argument("--check-status", action="store_true", help="Check server status and exit")
    parser.add_argument("--shutdown-server", action="store_true", help="Send shutdown signal to dashboard server")
    parser.add_argument("--cmd", type=str, help="Execute a specific command directly (open, pipeline, fetch, sync, status, quit)")
    args = parser.parse_args()

    if args.check_status:
        is_up = check_server_status()
        print(f"Dashboard ({DASHBOARD_URL}): {'ONLINE' if is_up else 'OFFLINE'}")
        sys.exit(0 if is_up else 1)

    if args.shutdown_server:
        quit_servers()
        return

    if args.cmd:
        handle_single_command(args.cmd)
        return

    if not args.cli:
        success = run_gui_tray()
        if not success:
            run_cli_daemon()
    else:
        run_cli_daemon()

if __name__ == "__main__":
    main()
