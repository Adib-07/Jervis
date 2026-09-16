from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from jarvis.system_tasks import (
    CAPABILITIES,
    Capability,
    battery_status,
    capabilities,
    current_time,
    list_workspace_files,
    open_app,
    open_folder,
    search_web,
)


class TestCapabilities:
    def test_capabilities_registry(self) -> None:
        assert isinstance(CAPABILITIES, tuple)
        assert len(CAPABILITIES) > 0

    def test_capability_fields(self) -> None:
        for cap in CAPABILITIES:
            assert isinstance(cap, Capability)
            assert cap.command
            assert cap.description
            assert len(cap.examples) > 0

    def test_capabilities_output(self) -> None:
        result = capabilities()
        assert "System tasks I can perform:" in result
        for cap in CAPABILITIES:
            assert cap.command in result


class TestCurrentTime:
    def test_current_time_format(self) -> None:
        result = current_time()
        assert result.startswith("It is")
        assert "2026" in result or "2025" in result or "2024" in result


class TestListWorkspaceFiles:
    def test_lists_files_in_directory(self, tmp_path: Path) -> None:
        (tmp_path / "file_a.txt").write_text("a")
        (tmp_path / "file_b.txt").write_text("b")
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        with patch("jarvis.system_tasks.Path.cwd", return_value=tmp_path):
            result = list_workspace_files()

        assert "file_a.txt" in result
        assert "file_b.txt" in result
        assert "subdir/" in result

    def test_empty_directory(self, tmp_path: Path) -> None:
        with patch("jarvis.system_tasks.Path.cwd", return_value=tmp_path):
            result = list_workspace_files()
        assert "No files found" in result


class TestOpenApp:
    def test_empty_name(self) -> None:
        result = open_app("")
        assert "Use `open app <name>`" in result

    @patch("jarvis.system_tasks.platform.system", return_value="Linux")
    def test_non_darwin(self, mock_system) -> None:
        result = open_app("Safari")
        assert "macOS" in result

    @patch("jarvis.system_tasks.platform.system", return_value="Darwin")
    @patch("jarvis.system_tasks.subprocess.run")
    def test_successful_open(self, mock_run, mock_system) -> None:
        mock_run.return_value = type("Result", (), {"returncode": 0, "stderr": "", "stdout": ""})()
        result = open_app("Safari")
        assert "Opened Safari" in result
        mock_run.assert_called_once_with(
            ["open", "-a", "Safari"],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("jarvis.system_tasks.platform.system", return_value="Darwin")
    @patch("jarvis.system_tasks.subprocess.run")
    def test_failed_open(self, mock_run, mock_system) -> None:
        mock_run.return_value = type(
            "Result", (), {"returncode": 1, "stderr": "No such app", "stdout": ""}
        )()
        result = open_app("FakeApp")
        assert "could not open FakeApp" in result


class TestOpenFolder:
    def test_empty_path(self, tmp_path: Path) -> None:
        with patch("jarvis.system_tasks.subprocess.run") as mock_run:
            mock_run.return_value = type("Result", (), {"returncode": 0, "stderr": "", "stdout": ""})()
            result = open_folder(".")
            assert "Opened folder" in result

    def test_nonexistent_folder(self) -> None:
        result = open_folder("/nonexistent/path/xyz")
        assert "does not exist" in result

    def test_not_a_directory(self, tmp_path: Path) -> None:
        file_path = tmp_path / "afile.txt"
        file_path.write_text("content")
        result = open_folder(str(file_path))
        assert "not a folder" in result


class TestSearchWeb:
    def test_empty_query(self) -> None:
        result = search_web("")
        assert "Use `search web for <query>`" in result

    @patch("jarvis.system_tasks.webbrowser.open")
    def test_search_opens_url(self, mock_open) -> None:
        result = search_web("python docs")
        assert "Searching the web for: python docs" in result
        mock_open.assert_called_once()
        url = mock_open.call_args[0][0]
        assert "python%20docs" in url or "python+docs" in url


class TestBatteryStatus:
    @patch("jarvis.system_tasks.platform.system", return_value="Linux")
    def test_non_darwin(self, mock_system) -> None:
        result = battery_status()
        assert "macOS" in result
