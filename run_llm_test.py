from jarvis.config import load_config
from jarvis.llm import LlmClient, LlmConfig

cfg = load_config()
client = LlmClient(LlmConfig(cfg.openai_api_key,
                   cfg.openai_model, cfg.ollama_url, cfg.ollama_model))
print("OLLAMA_URL:", cfg.ollama_url)
print("OLLAMA_MODEL:", cfg.ollama_model)
print("ollama_available:", client.ollama_available())
