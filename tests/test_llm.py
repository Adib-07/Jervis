from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from jarvis.llm import LlmClient, LlmConfig


class TestLlmConfig:
    def test_config_fields(self) -> None:
        cfg = LlmConfig(api_key="k", model="m", ollama_url="http://x", ollama_model="om")
        assert cfg.api_key == "k"
        assert cfg.model == "m"


class TestProviderSelection:
    def test_no_provider_configured(self) -> None:
        client = LlmClient(
            LlmConfig(api_key=None, model="m", ollama_url="http://x", ollama_model="om")
        )
        with patch.object(client, "ollama_available", return_value=False):
            result = client.complete("hello")
        assert "not configured" in result

    def test_openai_key_configured(self) -> None:
        client = LlmClient(
            LlmConfig(api_key="sk-test", model="m", ollama_url="http://x", ollama_model="om")
        )
        mock_response = MagicMock()
        mock_response.output_text = "OpenAI answer"
        mock_client = MagicMock()
        mock_client.responses.create.return_value = mock_response

        with patch.dict("sys.modules", {"openai": MagicMock(OpenAI=MagicMock(return_value=mock_client))}):
            result = client.complete("what is python")

        assert result == "OpenAI answer"

    def test_ollama_available_returns_tag(self) -> None:
        client = LlmClient(
            LlmConfig(api_key=None, model="m", ollama_url="http://x", ollama_model="om")
        )
        with patch("jarvis.llm.urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response
            assert client.ollama_available() is True

    def test_ollama_unavailable(self) -> None:
        client = LlmClient(
            LlmConfig(api_key=None, model="m", ollama_url="http://x", ollama_model="om")
        )
        with patch("jarvis.llm.urllib.request.urlopen", side_effect=OSError("refused")):
            assert client.ollama_available() is False

    def test_ollama_success_response(self) -> None:
        client = LlmClient(
            LlmConfig(api_key=None, model="m", ollama_url="http://x", ollama_model="om")
        )
        response_body = json.dumps({"message": {"content": "Ollama says hi"}}).encode()
        mock_response = MagicMock()
        mock_response.read.return_value = response_body
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("jarvis.llm.urllib.request.urlopen", return_value=mock_response):
            result = client.complete("hello")

        assert result == "Ollama says hi"

    def test_ollama_failure_falls_back(self) -> None:
        client = LlmClient(
            LlmConfig(api_key=None, model="m", ollama_url="http://x", ollama_model="om")
        )
        with patch("jarvis.llm.urllib.request.urlopen", side_effect=OSError("timeout")):
            result = client.complete("hello")
        assert "not configured" in result

    def test_ollama_bad_json_falls_back(self) -> None:
        client = LlmClient(
            LlmConfig(api_key=None, model="m", ollama_url="http://x", ollama_model="om")
        )
        mock_response = MagicMock()
        mock_response.read.return_value = b"not json"
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("jarvis.llm.urllib.request.urlopen", return_value=mock_response):
            result = client.complete("hello")
        assert "not configured" in result

    def test_ollama_no_message_field(self) -> None:
        client = LlmClient(
            LlmConfig(api_key=None, model="m", ollama_url="http://x", ollama_model="om")
        )
        response_body = json.dumps({"unexpected": "data"}).encode()
        mock_response = MagicMock()
        mock_response.read.return_value = response_body
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("jarvis.llm.urllib.request.urlopen", return_value=mock_response):
            result = client.complete("hello")
        assert "not configured" in result

    def test_available_property_with_key(self) -> None:
        client = LlmClient(
            LlmConfig(api_key="sk-test", model="m", ollama_url="http://x", ollama_model="om")
        )
        assert client.available is True

    def test_available_property_without_key_ollama_down(self) -> None:
        client = LlmClient(
            LlmConfig(api_key=None, model="m", ollama_url="http://x", ollama_model="om")
        )
        with patch.object(client, "ollama_available", return_value=False):
            assert client.available is False
