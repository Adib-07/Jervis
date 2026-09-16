from __future__ import annotations

from unittest.mock import patch

from jarvis.assistant import Assistant
from jarvis.tools import ToolContext


def _make_assistant(tool_ctx: ToolContext) -> Assistant:
    return Assistant(tool_ctx)


class TestRoutingHelp:
    def test_help(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("help")
        assert "Commands:" in result

    def test_help_question_mark(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("?")
        assert "Commands:" in result


class TestRoutingCapabilities:
    def test_capabilities(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("capabilities")
        assert "System tasks" in result

    def test_what_can_you_do(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("what can you do")
        assert "System tasks" in result


class TestRoutingStatus:
    def test_status(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("status")
        assert "OS:" in result


class TestRoutingApps:
    @patch("jarvis.assistant.list_apps", return_value="Installed apps:\n  Safari")
    def test_apps(self, mock_list_apps, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("apps")
        assert "Safari" in result
        mock_list_apps.assert_called_once()


class TestRoutingOpenApp:
    @patch("jarvis.assistant.open_app", return_value="Opened Safari.")
    def test_open_app(self, mock_open_app, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("open app Safari")
        mock_open_app.assert_called_once_with("Safari")
        assert "Opened Safari" in result

    @patch("jarvis.assistant.open_app", return_value="Opened Calculator.")
    def test_launch(self, mock_open_app, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("launch Calculator")
        mock_open_app.assert_called_once_with("Calculator")


class TestRoutingOpenFolder:
    @patch("jarvis.assistant.open_folder", return_value="Opened folder /tmp.")
    def test_open_folder(self, mock_open_folder, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("open folder /tmp")
        mock_open_folder.assert_called_once_with("/tmp")


class TestRoutingSearch:
    @patch("jarvis.assistant.search_web", return_value="Searching the web for: python")
    def test_search_web_for(self, mock_search, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("search web for python")
        mock_search.assert_called_once_with("python")

    @patch("jarvis.assistant.search_web", return_value="Searching the web for: news")
    def test_google(self, mock_search, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("google news")
        mock_search.assert_called_once_with("news")


class TestRoutingTimeDate:
    @patch("jarvis.assistant.current_time", return_value="It is Monday, 2024-01-01 12:00:00.")
    def test_time(self, mock_time, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("time")
        assert "Monday" in result

    @patch("jarvis.assistant.current_time", return_value="It is Monday, 2024-01-01 12:00:00.")
    def test_date(self, mock_time, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("date")
        mock_time.assert_called_once()


class TestRoutingBattery:
    @patch("jarvis.assistant.battery_status", return_value="Battery is 85% and charging.")
    def test_battery(self, mock_battery, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("battery")
        assert "85%" in result


class TestRoutingFiles:
    @patch("jarvis.assistant.list_workspace_files", return_value="Files in /tmp:")
    def test_files(self, mock_files, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("files")
        assert "Files in" in result


class TestRoutingMemory:
    def test_remember(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("remember buy eggs")
        assert "Remembered note #1" in result

    def test_notes(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("notes")
        assert "No notes saved yet" in result

    def test_forget(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        asst.handle("remember something")
        result = asst.handle("forget 1")
        assert "Deleted note #1" in result

    def test_reminders(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("reminders")
        assert "No active reminders" in result

    def test_done(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        asst.handle("remind me to run at 10:00")
        result = asst.handle("done 1")
        assert "Marked reminder #1 done" in result


class TestRoutingChat:
    @patch("jarvis.assistant.chat", return_value="AI response")
    def test_chat_explicit(self, mock_chat, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("chat what is python")
        mock_chat.assert_called_once_with(tool_ctx, "what is python")
        assert result == "AI response"

    @patch("jarvis.assistant.chat", return_value="fallback response")
    def test_fallback_to_chat(self, mock_chat, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("some random text")
        mock_chat.assert_called_once_with(tool_ctx, "some random text")


class TestRoutingEmpty:
    def test_empty_command(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("")
        assert "help" in result.lower()

    def test_whitespace_command(self, tool_ctx: ToolContext) -> None:
        asst = _make_assistant(tool_ctx)
        result = asst.handle("   ")
        assert "help" in result.lower()
