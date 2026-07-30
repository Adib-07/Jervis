from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import platform
import re
import subprocess
import urllib.parse
import webbrowser


@dataclass(frozen=True)
class Capability:
    command: str
    description: str
    examples: tuple[str, ...]


CAPABILITIES: tuple[Capability, ...] = (
    Capability(
        "capabilities",
        "List the system tasks Jarvis knows how to perform.",
        ("capabilities", "what can you do"),
    ),
    Capability(
        "apps",
        "List installed applications found in common application folders.",
        ("apps", "list apps"),
    ),
    Capability(
        "open app <name>",
        "Open a macOS application by name.",
        ("open app Safari", "launch calculator"),
    ),
    Capability(
        "open folder <path>",
        "Open a folder in Finder.",
        ("open folder .", "open folder ~/Downloads"),
    ),
    Capability(
        "search web for <query>",
        "Open the default browser with a web search.",
        ("search web for weather in Mumbai", "google Python speech recognition"),
    ),
    Capability(
        "time",
        "Show the current date and time.",
        ("time", "what time is it"),
    ),
    Capability(
        "battery",
        "Show battery status when available.",
        ("battery", "battery status"),
    ),
    Capability(
        "files",
        "List files in the current workspace directory.",
        ("files", "list files"),
    ),
)


def capabilities() -> str:
    lines = ["System tasks I can perform:"]
    for capability in CAPABILITIES:
        example = capability.examples[0]
        lines.append(f"  {capability.command}: {capability.description} Example: `{example}`")
    return "\n".join(lines)


def list_apps(limit: int = 80) -> str:
    app_dirs = [Path("/Applications"), Path.home() / "Applications"]
    apps: list[str] = []

    for app_dir in app_dirs:
        if not app_dir.exists():
            continue
        for app in app_dir.glob("*.app"):
            apps.append(app.stem)

    if not apps:
        return "I could not find applications in /Applications or ~/Applications."

    names = sorted(set(apps), key=str.lower)
    visible = names[:limit]
    suffix = "" if len(names) <= limit else f"\n...and {len(names) - limit} more."
    return "Installed apps:\n" + "\n".join(f"  {name}" for name in visible) + suffix


def open_app(name: str) -> str:
    app_name = name.strip()
    if not app_name:
        return "Use `open app <name>`."
    if platform.system() != "Darwin":
        return "Opening apps is currently implemented for macOS."

    result = subprocess.run(
        ["open", "-a", app_name],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return f"Opened {app_name}."
    detail = result.stderr.strip() or result.stdout.strip()
    return f"I could not open {app_name}. {detail}".strip()


def open_folder(raw_path: str) -> str:
    path_text = raw_path.strip() or "."
    path = Path(path_text).expanduser().resolve()
    if not path.exists():
        return f"Folder does not exist: {path}"
    if not path.is_dir():
        return f"That path is not a folder: {path}"

    result = subprocess.run(["open", str(path)], capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return f"Opened folder {path}."
    detail = result.stderr.strip() or result.stdout.strip()
    return f"I could not open {path}. {detail}".strip()


def search_web(query: str) -> str:
    cleaned = query.strip()
    if not cleaned:
        return "Use `search web for <query>`."
    encoded = urllib.parse.urlencode({"q": cleaned})
    webbrowser.open(f"https://www.google.com/search?{encoded}")
    return f"Searching the web for: {cleaned}"


def current_time() -> str:
    return datetime.now().strftime("It is %A, %Y-%m-%d %H:%M:%S.")


def battery_status() -> str:
    if platform.system() != "Darwin":
        return "Battery status is currently implemented for macOS."

    result = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        return f"I could not read battery status. {detail}".strip()

    output = " ".join(line.strip() for line in result.stdout.splitlines())
    percent = re.search(r"(\d+%)", output)
    charging = "charging" if "AC Power" in output else "not charging"
    if percent:
        return f"Battery is {percent.group(1)} and {charging}."
    return output or "Battery status is unavailable."


def list_workspace_files(limit: int = 80) -> str:
    root = Path.cwd()
    entries = sorted(root.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
    if not entries:
        return f"No files found in {root}."

    visible = entries[:limit]
    lines = [f"Files in {root}:"]
    for entry in visible:
        suffix = "/" if entry.is_dir() else ""
        lines.append(f"  {entry.name}{suffix}")
    if len(entries) > limit:
        lines.append(f"...and {len(entries) - limit} more.")
    return "\n".join(lines)
