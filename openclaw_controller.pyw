"""
OpenClaw Controller — System Tray Edition
- Lives in the system tray (bottom-right, arrow area)
- Right-click the tray icon for Start / Stop / Exit
- Icon turns green when running, red when stopped
- Rename to .pyw to run with no console window

Requires: pip install pystray pillow
"""

import subprocess
import time
import threading
from PIL import Image, ImageDraw
import pystray

OPENCLAW_CMD  = "openclaw"
OPENCLAW_PORT = 18789

# ── Process logic ────────────────────────────────────────────────────────────

_gateway_proc = None  # track the process we started

def start_gateway():
    global _gateway_proc
    # If already running (e.g. started by scheduled task), do nothing
    if _gateway_proc and _gateway_proc.poll() is None:
        return
    _gateway_proc = subprocess.Popen(
        ["cmd", "/c", f"{OPENCLAW_CMD} gateway start"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

def stop_gateway():
    global _gateway_proc
    # First try to stop gracefully via openclaw stop command
    subprocess.Popen(
        ["cmd", "/c", f"{OPENCLAW_CMD} gateway stop"],
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    # Kill only the process tree we spawned (not all node.exe on the system)
    if _gateway_proc and _gateway_proc.poll() is None:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(_gateway_proc.pid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    _gateway_proc = None

def get_status() -> str:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"(Get-NetTCPConnection -LocalPort {OPENCLAW_PORT} "
             f"-State Listen -ErrorAction SilentlyContinue) -ne $null"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        return "running" if result.stdout.strip().lower() == "true" else "stopped"
    except Exception:
        return "unknown"

# ── Tray icon drawing ─────────────────────────────────────────────────────────

def make_icon(status: str) -> Image.Image:
    """
    Draw a 64x64 tray icon:
      - Dark background
      - Colored circle: green=running, red=stopped, amber=unknown
      - Small lobster-claw notch cut out of the circle for style
    """
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background rounded square
    draw.rounded_rectangle([0, 0, size-1, size-1], radius=14,
                            fill=(22, 24, 30, 255))

    # Status color
    if status == "running":
        color = (0, 232, 150, 255)      # green
        ring  = (0, 180, 110, 180)
    elif status == "stopped":
        color = (255, 77, 58, 255)       # coral red
        ring  = (180, 40, 20, 180)
    else:
        color = (255, 179, 71, 255)      # amber
        ring  = (180, 120, 30, 180)

    # Outer ring
    draw.ellipse([8, 8, 55, 55], outline=ring, width=2)
    # Filled circle
    draw.ellipse([14, 14, 49, 49], fill=color)

    # Small dark cutout (claw notch) — gives it character
    draw.ellipse([34, 12, 48, 26], fill=(22, 24, 30, 255))
    draw.ellipse([38, 16, 46, 24], fill=color)

    return img

# ── Status polling loop ───────────────────────────────────────────────────────

_tray_icon = None   # set after creation

def _update_icon_loop():
    """Background thread — polls status every 8s and updates tray icon + tooltip."""
    while True:
        s = get_status()
        if _tray_icon:
            _tray_icon.icon  = make_icon(s)
            _tray_icon.title = f"OpenClaw  •  {s.capitalize()}"
        time.sleep(8)

# ── Menu actions ──────────────────────────────────────────────────────────────

def on_start(icon, item):
    def worker():
        icon.title = "OpenClaw  •  Starting…"
        icon.icon  = make_icon("unknown")
        start_gateway()
        time.sleep(4)
        s = get_status()
        icon.icon  = make_icon(s)
        icon.title = f"OpenClaw  •  {s.capitalize()}"
    threading.Thread(target=worker, daemon=True).start()

def on_stop(icon, item):
    def worker():
        icon.title = "OpenClaw  •  Stopping…"
        icon.icon  = make_icon("unknown")
        stop_gateway()
        time.sleep(3)
        s = get_status()
        icon.icon  = make_icon(s)
        icon.title = f"OpenClaw  •  {s.capitalize()}"
    threading.Thread(target=worker, daemon=True).start()

def on_exit(icon, item):
    icon.stop()

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    initial_status = get_status()

    menu = pystray.Menu(
        pystray.MenuItem("🦞  OpenClaw Gateway", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("▶  Start", on_start),
        pystray.MenuItem("■  Stop",  on_stop),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("✕  Exit",  on_exit),
    )

    _tray_icon = pystray.Icon(
        name="OpenClaw",
        icon=make_icon(initial_status),
        title=f"OpenClaw  •  {initial_status.capitalize()}",
        menu=menu,
    )

    # Start background status polling
    t = threading.Thread(target=_update_icon_loop, daemon=True)
    t.start()

    # Run tray (blocks until Exit is clicked)
    _tray_icon.run()