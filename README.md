# Jarvis

A small local assistant foundation inspired by J.A.R.V.I.S.

This project starts as a voice-first local assistant with:

- Microphone input
- Spoken responses
- Typed fallback mode
- Natural-language-ish command routing
- Local system task execution with a visible capability list
- Local SQLite memory for notes and reminders
- System information tools
- Optional OpenAI-powered chat when `OPENAI_API_KEY` is configured

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jarvis.web
```

This starts the local web app and opens it in your browser.

On macOS, microphone input may also need PyAudio:

```bash
brew install portaudio
python -m pip install -r requirements.txt
```

OpenAI integration is optional:

```bash
export OPENAI_API_KEY="your_api_key"
python -m jarvis
```

Typed-only fallback:

```bash
python -m jarvis --text
```

## Example Commands

```text
help
capabilities
apps
open app Calculator
open folder ~/Downloads
search web for Python speech recognition
battery
status
remember my passport is in the blue drawer
notes
remind me to drink water at 18:30
reminders
forget 1
chat draft a short email asking for a meeting
exit
```

When running in voice mode, say one command at a time. Say "exit" or "quit" to stop.

## Project Layout

```text
jarvis/
  __main__.py      # Module entrypoint
  assistant.py     # Main assistant loop and routing
  config.py        # Runtime configuration
  llm.py           # Optional OpenAI client wrapper
  memory.py        # SQLite-backed notes/reminders
  system_tasks.py  # Local system task capability registry
  tools.py         # Built-in command handlers
```

## Current System Task Scope

Jarvis can currently:

- List its supported capabilities.
- List installed macOS apps from `/Applications` and `~/Applications`.
- Open a named macOS app.
- Open a folder in Finder.
- Start a web search in the default browser.
- Report date/time, disk, OS, and battery information.
- List files in the current workspace.

The first version intentionally does not run arbitrary shell commands from voice input. Add new task handlers in `jarvis/system_tasks.py` when you want Jarvis to control more of the system.

## Next Useful Milestones

1. Add confirmation prompts for actions like sending messages or deleting files.
2. Add calendar/email integrations.
3. Add a browser or desktop automation tool layer.
4. Add a web dashboard.
5. Add background reminder notifications.
