from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

from jarvis.web import JarvisWebHandler


def _make_handler(path: str, method: str = "GET", body: bytes = b"") -> JarvisWebHandler:
    handler = MagicMock(spec=JarvisWebHandler)
    handler.path = path
    handler.headers = {"Content-Length": str(len(body))}
    handler.rfile = BytesIO(body)
    handler.wfile = BytesIO()

    def send_response(code):
        handler._status_code = code

    def send_header(key, val):
        pass

    def end_headers():
        pass

    handler.send_response = send_response
    handler.send_header = send_header
    handler.end_headers = end_headers

    handler._send_json = JarvisWebHandler._send_json.__get__(handler)
    handler._read_json = JarvisWebHandler._read_json.__get__(handler)
    handler.log_message = lambda *a: None

    return handler


class TestHealthEndpoint:
    def test_health_returns_json(self) -> None:
        handler = _make_handler("/health")
        with patch.object(JarvisWebHandler, "do_GET", wraps=JarvisWebHandler.do_GET):
            handler.assistant = MagicMock()
            handler.assistant.context.llm.available = False
            handler.listener = MagicMock()
            handler.listener.available = False

            JarvisWebHandler.do_GET(handler)

        handler.wfile.seek(0)
        data = json.loads(handler.wfile.read().decode())
        assert data["ok"] is True
        assert "voice" in data
        assert "ai" in data


class TestCommandEndpoint:
    def test_valid_command(self) -> None:
        body = json.dumps({"command": "help"}).encode()
        handler = _make_handler("/api/command", method="POST", body=body)
        handler.assistant = MagicMock()
        handler.assistant.handle.return_value = "Commands: ..."

        JarvisWebHandler._handle_command(handler)

        handler.wfile.seek(0)
        data = json.loads(handler.wfile.read().decode())
        assert data["ok"] is True
        assert data["command"] == "help"

    def test_invalid_json(self) -> None:
        handler = _make_handler("/api/command", method="POST", body=b"not json {{{")
        handler.assistant = MagicMock()

        JarvisWebHandler._handle_command(handler)

        handler.wfile.seek(0)
        data = json.loads(handler.wfile.read().decode())
        assert data["ok"] is False
        assert handler._status_code == 400

    def test_non_dict_body(self) -> None:
        handler = _make_handler("/api/command", method="POST", body=b'[1, 2, 3]')
        handler.assistant = MagicMock()

        JarvisWebHandler._handle_command(handler)

        handler.wfile.seek(0)
        data = json.loads(handler.wfile.read().decode())
        assert data["ok"] is False

    def test_empty_command(self) -> None:
        body = json.dumps({"command": ""}).encode()
        handler = _make_handler("/api/command", method="POST", body=body)
        handler.assistant = MagicMock()
        handler.assistant.handle.return_value = "Say `help` to see what I can do."

        JarvisWebHandler._handle_command(handler)

        handler.wfile.seek(0)
        data = json.loads(handler.wfile.read().decode())
        assert data["ok"] is True


class TestSpeakEndpoint:
    def test_speak_empty_text(self) -> None:
        body = json.dumps({"text": ""}).encode()
        handler = _make_handler("/api/speak", method="POST", body=body)

        JarvisWebHandler._handle_speak(handler)

        handler.wfile.seek(0)
        data = json.loads(handler.wfile.read().decode())
        assert data["ok"] is False
        assert handler._status_code == 400

    def test_speak_valid_text(self) -> None:
        body = json.dumps({"text": "hello world"}).encode()
        handler = _make_handler("/api/speak", method="POST", body=body)

        with patch("jarvis.web.subprocess.Popen"):
            JarvisWebHandler._handle_speak(handler)

        handler.wfile.seek(0)
        data = json.loads(handler.wfile.read().decode())
        assert data["ok"] is True

    def test_speak_invalid_json(self) -> None:
        handler = _make_handler("/api/speak", method="POST", body=b"bad")

        JarvisWebHandler._handle_speak(handler)

        handler.wfile.seek(0)
        data = json.loads(handler.wfile.read().decode())
        assert data["ok"] is False
        assert handler._status_code == 400


class TestPostRouting:
    def test_unknown_post_returns_404(self) -> None:
        handler = _make_handler("/api/unknown", method="POST")
        handler.send_error = MagicMock()

        JarvisWebHandler.do_POST(handler)

        handler.send_error.assert_called_once_with(404)
