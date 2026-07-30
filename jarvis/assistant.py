from __future__ import annotations

import argparse

from jarvis.config import load_config
from jarvis.llm import LlmClient, LlmConfig
from jarvis.memory import MemoryStore
from jarvis.system_tasks import (
    battery_status,
    capabilities,
    current_time,
    list_apps,
    list_workspace_files,
    open_app,
    open_folder,
    search_web,
)
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
from jarvis.voice import Listener, Speaker


class Assistant:
    def __init__(self, context: ToolContext) -> None:
        self.context = context

    def handle(self, command: str) -> str:
        command = command.strip()
        lowered = command.lower()

        if not command:
            return "Say `help` to see what I can do."
        if lowered in {"help", "?"}:
            return help_text()
        if lowered in {"capabilities", "what can you do", "what tasks can you perform"}:
            return capabilities()
        if lowered == "status":
            return status()
        if lowered in {"apps", "list apps", "list applications"}:
            return list_apps()
        if lowered.startswith("open app "):
            return open_app(command.removeprefix("open app ").strip())
        if lowered.startswith("launch "):
            return open_app(command.removeprefix("launch ").strip())
        if lowered.startswith("open folder "):
            return open_folder(command.removeprefix("open folder ").strip())
        if lowered.startswith("search web for "):
            return search_web(command.removeprefix("search web for ").strip())
        if lowered.startswith("google "):
            return search_web(command.removeprefix("google ").strip())
        if lowered in {"time", "what time is it", "date"}:
            return current_time()
        if lowered in {"battery", "battery status"}:
            return battery_status()
        if lowered in {"files", "list files"}:
            return list_workspace_files()
        if lowered.startswith("remember "):
            return remember(self.context, command.removeprefix("remember ").strip())
        if lowered == "notes":
            return notes(self.context)
        if lowered.startswith("forget "):
            return forget(self.context, command.removeprefix("forget "))
        if lowered.startswith("remind me to "):
            return remind(self.context, command)
        if lowered == "reminders":
            return reminders(self.context)
        if lowered.startswith("done "):
            return done(self.context, command.removeprefix("done "))
        if lowered.startswith("chat "):
            return chat(self.context, command.removeprefix("chat ").strip())

        return chat(self.context, command)


def build_assistant() -> Assistant:
    config = load_config()
    memory = MemoryStore(config.database_path)
    llm = LlmClient(
        LlmConfig(
            config.openai_api_key,
            config.openai_model,
            config.ollama_url,
            config.ollama_model,
        )
    )
    return Assistant(ToolContext(memory=memory, llm=llm))


def run_text_loop(assistant: Assistant) -> None:
    print("Jarvis online. Type `help` for commands or `exit` to quit.")

    while True:
        try:
            command = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return

        if command.strip().lower() in {"exit", "quit"}:
            print("Goodbye.")
            return

        print(assistant.handle(command))


def run_voice_loop(assistant: Assistant) -> None:
    speaker = Speaker()
    listener = Listener()

    if not listener.available:
        print(f"Voice input is unavailable: {listener.error}")
        print("Starting typed fallback.")
        run_text_loop(assistant)
        return

    if speaker.available:
        speaker.say("Jarvis online.")
    else:
        print(f"Voice output is unavailable: {speaker.error}")
        print("Jarvis online.")

    print("Say `help` for commands or `exit` to quit.")

    while True:
        heard = listener.listen()
        if heard.error:
            print(f"Could not understand audio: {heard.error}")
            continue

        command = heard.text
        print(f"You said: {command}")

        if command.strip().lower() in {"exit", "quit"}:
            speaker.say("Goodbye.")
            return

        speaker.say(assistant.handle(command))


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis voice assistant")
    parser.add_argument(
        "--text",
        action="store_true",
        help="Use typed input instead of microphone input.",
    )
    args = parser.parse_args()

    assistant = build_assistant()
    if args.text:
        run_text_loop(assistant)
    else:
        run_voice_loop(assistant)
