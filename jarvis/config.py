from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Config:
    data_dir: Path
    database_path: Path
    openai_api_key: str | None
    openai_model: str
    ollama_url: str
    ollama_model: str


def load_config() -> Config:
    data_dir = Path(os.environ.get("JARVIS_DATA_DIR", ".jarvis_data")).resolve()
    return Config(
        data_dir=data_dir,
        database_path=data_dir / "memory.sqlite3",
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        openai_model=os.environ.get("JARVIS_OPENAI_MODEL", "gpt-4.1-mini"),
        ollama_url=os.environ.get("JARVIS_OLLAMA_URL", "http://127.0.0.1:11434"),
        ollama_model=os.environ.get("JARVIS_OLLAMA_MODEL", "llama3.2"),
    )
