from __future__ import annotations

from unittest.mock import MagicMock, patch

from jarvis.tools import (
    ToolContext,
    chat,
    done,
    forget,
    help_text,
    notes,
    remember,
    reminders,
    remind,
    status,
)


class TestHelp:
    def test_help_contains_commands(self) -> None:
        text = help_text()
        assert "Commands:" in text
        assert "remember" in text
        assert "notes" in text
        assert "reminders" in text

    def test_help_contains_capabilities(self) -> None:
        text = help_text()
        assert "System tasks" in text


class TestStatus:
    def test_status_contains_os(self) -> None:
        result = status()
        assert "OS:" in result
        assert "Python:" in result
        assert "Disk free:" in result
        assert "Time:" in result


class TestRemember:
    def test_remember_saves_note(self, tool_ctx: ToolContext) -> None:
        result = remember(tool_ctx, "my test note")
        assert "Remembered note #1" in result

    def test_remember_empty_body(self, tool_ctx: ToolContext) -> None:
        result = remember(tool_ctx, "")
        assert "Tell me what to remember" in result


class TestNotes:
    def test_notes_empty(self, tool_ctx: ToolContext) -> None:
        result = notes(tool_ctx)
        assert "No notes saved yet" in result

    def test_notes_with_content(self, tool_ctx: ToolContext) -> None:
        remember(tool_ctx, "first note")
        remember(tool_ctx, "second note")
        result = notes(tool_ctx)
        assert "first note" in result
        assert "second note" in result


class TestForget:
    def test_forget_existing_note(self, tool_ctx: ToolContext) -> None:
        remember(tool_ctx, "to forget")
        result = forget(tool_ctx, "1")
        assert "Deleted note #1" in result

    def test_forget_nonexistent_note(self, tool_ctx: ToolContext) -> None:
        result = forget(tool_ctx, "999")
        assert "No note found" in result

    def test_forget_invalid_id(self, tool_ctx: ToolContext) -> None:
        result = forget(tool_ctx, "abc")
        assert "Use `forget <note_id>`" in result


class TestRemind:
    def test_remind_saves(self, tool_ctx: ToolContext) -> None:
        result = remind(tool_ctx, "remind me to drink water at 18:30")
        assert "Reminder #1 saved for 18:30" in result

    def test_remind_bad_format(self, tool_ctx: ToolContext) -> None:
        result = remind(tool_ctx, "remind me something")
        assert "Use `remind me to <task> at <time>`" in result


class TestReminders:
    def test_reminders_empty(self, tool_ctx: ToolContext) -> None:
        result = reminders(tool_ctx)
        assert "No active reminders" in result

    def test_reminders_with_content(self, tool_ctx: ToolContext) -> None:
        remind(tool_ctx, "remind me to code at 09:00")
        result = reminders(tool_ctx)
        assert "code at 09:00" in result


class TestDone:
    def test_done_existing_reminder(self, tool_ctx: ToolContext) -> None:
        remind(tool_ctx, "remind me to review at 10:00")
        result = done(tool_ctx, "1")
        assert "Marked reminder #1 done" in result

    def test_done_nonexistent_reminder(self, tool_ctx: ToolContext) -> None:
        result = done(tool_ctx, "999")
        assert "No reminder found" in result

    def test_done_invalid_id(self, tool_ctx: ToolContext) -> None:
        result = done(tool_ctx, "abc")
        assert "Use `done <reminder_id>`" in result


class TestChat:
    def test_chat_empty_prompt(self, tool_ctx: ToolContext) -> None:
        result = chat(tool_ctx, "")
        assert "Use `chat <prompt>`" in result

    def test_chat_delegates_to_llm(self, tool_ctx: ToolContext) -> None:
        tool_ctx.llm.complete = MagicMock(return_value="AI response here")
        result = chat(tool_ctx, "hello")
        tool_ctx.llm.complete.assert_called_once_with("hello")
        assert result == "AI response here"
