from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import webbrowser

from jarvis.assistant import build_assistant
from jarvis.voice import Listener


ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = ROOT / "web"


class JarvisWebHandler(SimpleHTTPRequestHandler):
    assistant = build_assistant()
    listener = Listener()

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(
                {
                    "ok": True,
                    "voice": self.listener.available,
                    "ai": self.assistant.context.llm.available,
                }
            )
            return
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        if self.path == "/api/command":
            self._handle_command()
            return
        if self.path == "/api/listen":
            self._handle_listen()
            return
        if self.path == "/api/speak":
            self._handle_speak()
            return
        self.send_error(404)

    def _handle_command(self) -> None:
        body = self._read_json()
        if body is None:
            self._send_json({"ok": False, "response": "Invalid request."}, status=400)
            return

        command = str(body.get("command", "")).strip()
        response = self.assistant.handle(command)
        self._send_json({"ok": True, "command": command, "response": response})

    def _handle_listen(self) -> None:
        if not self.listener.available:
            self._send_json(
                {
                    "ok": False,
                    "error": self.listener.error or "Microphone input is unavailable.",
                },
                status=503,
            )
            return

        heard = self.listener.listen(timeout=6, phrase_time_limit=9)
        if heard.error:
            self._send_json({"ok": False, "error": heard.error}, status=422)
            return

        command = heard.text.strip()
        if not command:
            self._send_json({"ok": False, "error": "I did not hear a command."}, status=422)
            return

        response = self.assistant.handle(command)
        self._send_json({"ok": True, "command": command, "response": response})

    def _handle_speak(self) -> None:
        body = self._read_json()
        if body is None:
            self._send_json({"ok": False, "error": "Invalid request."}, status=400)
            return

        text = str(body.get("text", "")).strip()
        if not text:
            self._send_json({"ok": False, "error": "No speech text provided."}, status=400)
            return

        subprocess.Popen(["say", text[:1200]])
        self._send_json({"ok": True})

    def _read_json(self) -> dict[str, object] | None:
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length)
        try:
            body = json.loads(payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
        if not isinstance(body, dict):
            return None
        return body

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), JarvisWebHandler)
    port = server.server_port
    url = f"http://127.0.0.1:{port}"
    print(f"Jarvis web app running at {url}")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Jarvis web app.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
