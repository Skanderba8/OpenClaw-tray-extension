# 🦞 OpenClaw Tray Controller

A lightweight Windows system tray extension to start and stop the [OpenClaw](https://openclaw.ai) gateway without ever opening a terminal.

---

## What it does

- Sits silently in your **system tray** (bottom-right, near the clock)
- **Right-click** the icon to Start, Stop, or Exit
- Icon changes color based on gateway status — 🟢 running, 🔴 stopped
- Status auto-refreshes every 8 seconds
- No terminal window, no console, just works in the background

---

## Requirements

- Windows 10 or 11
- Python 3.x — [download here](https://python.org/downloads)
- OpenClaw installed — [docs here](https://docs.openclaw.ai)
- Two Python packages:

```bash
pip install pystray pillow
```

---

## Setup

**1. Clone or download this repo**

```bash
https://github.com/Skanderba8/OpenClaw-tray-extension
```

**2. Rename the file**

Rename `openclaw_controller.py` to `openclaw_controller.pyw` — this tells Windows to run it with no console window.

**3. Run it**

Double-click `openclaw_controller.pyw`. The icon will appear in your system tray.

---

## Auto-start on boot

To have it launch automatically every time you start your PC:

1. Press `Win + R`, type `shell:startup`, press Enter
2. Right-click `openclaw_controller.pyw` and create a shortcut
3. Move the shortcut into the startup folder

---

## Usage

Right-click the tray icon to access the menu:

| Option | Description |
|--------|-------------|
| ▶ Start | Launches the OpenClaw gateway |
| ■ Stop | Stops the gateway and cleans up processes |
| ✕ Exit | Closes the tray controller |

> Closing the tray controller does **not** stop the gateway. Use Stop first if you want to shut it down.

---

## Configuration

Open the file and edit these two lines at the top if needed:

```python
OPENCLAW_CMD  = "openclaw"   # full path if openclaw isn't on your PATH
OPENCLAW_PORT = 18789        # change if you're using a different port
```

---

## Built with

- [`pystray`](https://github.com/moses-palmer/pystray) — system tray integration
- [`Pillow`](https://python-pillow.org/) — icon rendering
- `subprocess` — process management

---

Made by **SkanderBA**
