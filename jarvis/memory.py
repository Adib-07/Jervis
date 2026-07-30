from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class Note:
    id: int
    body: str
    created_at: str


@dataclass(frozen=True)
class Reminder:
    id: int
    body: str
    remind_at: str
    created_at: str
    done: bool


class MemoryStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    body TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    body TEXT NOT NULL,
                    remind_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def add_note(self, body: str) -> Note:
        created_at = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO notes (body, created_at) VALUES (?, ?)",
                (body, created_at),
            )
            note_id = int(cursor.lastrowid)
        return Note(note_id, body, created_at)

    def list_notes(self) -> list[Note]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, body, created_at FROM notes ORDER BY id DESC"
            ).fetchall()
        return [Note(int(row["id"]), row["body"], row["created_at"]) for row in rows]

    def delete_note(self, note_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            return cursor.rowcount > 0

    def add_reminder(self, body: str, remind_at: str) -> Reminder:
        created_at = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO reminders (body, remind_at, created_at, done)
                VALUES (?, ?, ?, 0)
                """,
                (body, remind_at, created_at),
            )
            reminder_id = int(cursor.lastrowid)
        return Reminder(reminder_id, body, remind_at, created_at, False)

    def list_reminders(self, include_done: bool = False) -> list[Reminder]:
        query = """
            SELECT id, body, remind_at, created_at, done
            FROM reminders
        """
        params: tuple[object, ...] = ()
        if not include_done:
            query += " WHERE done = ?"
            params = (0,)
        query += " ORDER BY remind_at ASC, id ASC"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            Reminder(
                int(row["id"]),
                row["body"],
                row["remind_at"],
                row["created_at"],
                bool(row["done"]),
            )
            for row in rows
        ]

    def mark_reminder_done(self, reminder_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE reminders SET done = 1 WHERE id = ?",
                (reminder_id,),
            )
            return cursor.rowcount > 0
