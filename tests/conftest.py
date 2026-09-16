from __future__ import annotations

from pathlib import Path
from typing import Generator

import pytest

from jarvis.memory import MemoryStore
from jarvis.llm import LlmClient, LlmConfig
from jarvis.tools import ToolContext


@pytest.fixture()
def tmp_db(tmp_path: Path) -> Generator[MemoryStore, None, None]:
    db_path = tmp_path / "test_memory.sqlite3"
    store = MemoryStore(db_path)
    yield store


@pytest.fixture()
def fake_llm() -> LlmClient:
    return LlmClient(
        LlmConfig(
            api_key=None,
            model="test-model",
            ollama_url="http://127.0.0.1:11434",
            ollama_model="test-model",
        )
    )


@pytest.fixture()
def tool_ctx(tmp_db: MemoryStore, fake_llm: LlmClient) -> ToolContext:
    return ToolContext(memory=tmp_db, llm=fake_llm)
