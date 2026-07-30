from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import platform
import re
import shutil

from jarvis.llm import LlmClient
from jarvis.memory import MemoryStore
from jarvis.system_tasks import capabilities


@dataclass
class ToolContext:
    memory: MemoryStore
    llm: LlmClient


def help_text() -> str:
    return "\n".join(
        [
            "Commands:",
            "  help                         Show this help",
            "  capabilities                 Show system tasks Jarvis can perform",
            "  status                       Show system status",
            "  remember <text>              Save a note",
            "  notes                        List saved notes",
            "  forget <note_id>             Delete a note",
            "  remind me to <task> at <t>   Save a reminder",
            "  reminders                    List active reminders",
            "  done <reminder_id>           Mark a reminder done",
            "  chat <prompt>                Ask the optional OpenAI assistant",
            "  exit                         Quit",
            "",
            capabilities(),
        ]
    )


def status() -> str:
    total, used, free = shutil.disk_usage(".")
    return "\n".join(
        [
            f"OS: {platform.system()} {platform.release()}",
            f"Machine: {platform.machine()}",
            f"Python: {platform.python_version()}",
            f"Disk free: {_bytes_to_gb(free)} GB / {_bytes_to_gb(total)} GB",
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]
    )


def remember(ctx: ToolContext, body: str) -> str:
    if not body:
        return "Tell me what to remember."
    note = ctx.memory.add_note(body)
    return f"Remembered note #{note.id}."


def notes(ctx: ToolContext) -> str:
    saved = ctx.memory.list_notes()
    if not saved:
        return "No notes saved yet."
    return "\n".join(f"#{note.id}: {note.body} ({note.created_at})" for note in saved)


def forget(ctx: ToolContext, raw_id: str) -> str:
    try:
        note_id = int(raw_id.strip())
    except ValueError:
        return "Use `forget <note_id>`."
    if ctx.memory.delete_note(note_id):
        return f"Deleted note #{note_id}."
    return f"No note found with id #{note_id}."


def remind(ctx: ToolContext, command: str) -> str:
    match = re.match(r"remind me to (.+?) at (.+)$", command, flags=re.IGNORECASE)
    if not match:
        return "Use `remind me to <task> at <time>`."
    body = match.group(1).strip()
    remind_at = match.group(2).strip()
    reminder = ctx.memory.add_reminder(body, remind_at)
    return f"Reminder #{reminder.id} saved for {reminder.remind_at}."


def reminders(ctx: ToolContext) -> str:
    active = ctx.memory.list_reminders()
    if not active:
        return "No active reminders."
    return "\n".join(
        f"#{reminder.id}: {reminder.body} at {reminder.remind_at}"
        for reminder in active
    )


def done(ctx: ToolContext, raw_id: str) -> str:
    try:
        reminder_id = int(raw_id.strip())
    except ValueError:
        return "Use `done <reminder_id>`."
    if ctx.memory.mark_reminder_done(reminder_id):
        return f"Marked reminder #{reminder_id} done."
    return f"No reminder found with id #{reminder_id}."


def chat(ctx: ToolContext, prompt: str) -> str:
    if not prompt:
        return "Use `chat <prompt>`."
    return ctx.llm.complete(prompt)


def _bytes_to_gb(value: int) -> str:
    return f"{value / 1024 / 1024 / 1024:.1f}"
