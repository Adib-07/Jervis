from __future__ import annotations

from dataclasses import dataclass
import json
import urllib.error
import urllib.request


@dataclass(frozen=True)
class LlmConfig:
    api_key: str | None
    model: str
    ollama_url: str
    ollama_model: str


class LlmClient:
    def __init__(self, config: LlmConfig) -> None:
        self.config = config
        self._client = None

    @property
    def available(self) -> bool:
        return bool(self.config.api_key) or self.ollama_available()

    def complete(self, prompt: str) -> str:
        if self.config.api_key:
            return self._complete_openai(prompt)

        ollama_response = self._complete_ollama(prompt)
        if ollama_response is not None:
            return ollama_response

        return (
            "AI chat is not configured yet. To answer general questions, either start "
            "Ollama with a model such as `llama3.2`, or set OPENAI_API_KEY before "
            "running Jarvis."
        )

    def ollama_available(self) -> bool:
        try:
            request = urllib.request.Request(
                f"{self.config.ollama_url}/api/tags")
            with urllib.request.urlopen(request, timeout=1.5) as response:
                return response.status == 200
        except (OSError, urllib.error.URLError):
            return False

    def _complete_openai(self, prompt: str) -> str:
        if not self.config.api_key:
            return (
                "OpenAI chat is not configured. Set OPENAI_API_KEY, then try the "
                "`chat ...` command again."
            )

        try:
            from openai import OpenAI
        except ImportError:
            return "The `openai` package is not installed. Run `python -m pip install -r requirements.txt`."

        if self._client is None:
            self._client = OpenAI(api_key=self.config.api_key)

        response = self._client.responses.create(
            model=self.config.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, a concise local AI assistant. Be practical, "
                        "specific, and helpful."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.output_text.strip()

    def _complete_ollama(self, prompt: str) -> str | None:
        payload = {
            "model": self.config.ollama_model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, a concise desktop AI assistant. Answer normal "
                        "questions directly. When the user asks for system control, tell "
                        "them the exact Jarvis command if one exists."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.config.ollama_url}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError):
            return None

        message = body.get("message")
        if not isinstance(message, dict):
            return None
        content = message.get("content")
        if not isinstance(content, str):
            return None
        return content.strip()
