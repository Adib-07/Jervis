from __future__ import annotations

from pathlib import Path

from jarvis.memory import MemoryStore, Note, Reminder


class TestDatabaseInit:
    def test_creates_database_file(self, tmp_path: Path) -> None:
        db_path = tmp_path / "mem.sqlite3"
        assert not db_path.exists()
        MemoryStore(db_path)
        assert db_path.exists()

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        db_path = tmp_path / "nested" / "dir" / "mem.sqlite3"
        MemoryStore(db_path)
        assert db_path.exists()

    def test_reopen_existing_database(self, tmp_path: Path) -> None:
        db_path = tmp_path / "mem.sqlite3"
        store = MemoryStore(db_path)
        store.add_note("persisted")
        store2 = MemoryStore(db_path)
        notes = store2.list_notes()
        assert len(notes) == 1
        assert notes[0].body == "persisted"


class TestNotes:
    def test_add_note_returns_note(self, tmp_db: MemoryStore) -> None:
        note = tmp_db.add_note("buy milk")
        assert isinstance(note, Note)
        assert note.body == "buy milk"
        assert note.id >= 1

    def test_list_notes_empty(self, tmp_db: MemoryStore) -> None:
        assert tmp_db.list_notes() == []

    def test_list_notes_returns_all(self, tmp_db: MemoryStore) -> None:
        tmp_db.add_note("first")
        tmp_db.add_note("second")
        notes = tmp_db.list_notes()
        assert len(notes) == 2
        assert notes[0].body == "second"
        assert notes[1].body == "first"

    def test_delete_note_existing(self, tmp_db: MemoryStore) -> None:
        note = tmp_db.add_note("to delete")
        assert tmp_db.delete_note(note.id) is True
        assert tmp_db.list_notes() == []

    def test_delete_note_nonexistent(self, tmp_db: MemoryStore) -> None:
        assert tmp_db.delete_note(9999) is False

    def test_note_has_created_at(self, tmp_db: MemoryStore) -> None:
        note = tmp_db.add_note("timestamped")
        assert note.created_at
        assert len(note.created_at) > 0


class TestReminders:
    def test_add_reminder(self, tmp_db: MemoryStore) -> None:
        reminder = tmp_db.add_reminder("drink water", "18:30")
        assert isinstance(reminder, Reminder)
        assert reminder.body == "drink water"
        assert reminder.remind_at == "18:30"
        assert reminder.done is False

    def test_list_reminders_empty(self, tmp_db: MemoryStore) -> None:
        assert tmp_db.list_reminders() == []

    def test_list_reminders_active_only(self, tmp_db: MemoryStore) -> None:
        r1 = tmp_db.add_reminder("task one", "09:00")
        r2 = tmp_db.add_reminder("task two", "10:00")
        tmp_db.mark_reminder_done(r1.id)
        active = tmp_db.list_reminders()
        assert len(active) == 1
        assert active[0].id == r2.id

    def test_list_reminders_include_done(self, tmp_db: MemoryStore) -> None:
        r1 = tmp_db.add_reminder("task one", "09:00")
        tmp_db.mark_reminder_done(r1.id)
        all_reminders = tmp_db.list_reminders(include_done=True)
        assert len(all_reminders) == 1
        assert all_reminders[0].done is True

    def test_mark_reminder_done(self, tmp_db: MemoryStore) -> None:
        reminder = tmp_db.add_reminder("finish report", "17:00")
        assert tmp_db.mark_reminder_done(reminder.id) is True
        active = tmp_db.list_reminders()
        assert len(active) == 0

    def test_mark_nonexistent_reminder_done(self, tmp_db: MemoryStore) -> None:
        assert tmp_db.mark_reminder_done(9999) is False

    def test_reminder_ordering(self, tmp_db: MemoryStore) -> None:
        tmp_db.add_reminder("later", "10:00")
        tmp_db.add_reminder("earlier", "09:00")
        reminders = tmp_db.list_reminders()
        assert reminders[0].remind_at == "09:00"
        assert reminders[1].remind_at == "10:00"
