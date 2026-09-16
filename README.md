# Jervis

A local voice-first desktop assistant with optional AI chat, built in Python.

## Overview

Jervis is a lightweight personal assistant that runs entirely on your machine. It accepts commands through a terminal, a local web interface, or your microphone, then routes them through a simple command handler to perform system tasks, manage notes and reminders, or delegate general questions to an external LLM provider.

The implementation is intentionally small: a single command router, a handful of tool handlers, a SQLite store, and optional integrations with OpenAI and Ollama. There is no framework overhead, no background daemon, and no cloud dependency for core functionality.

## Key Capabilities

| Category | What it does |
|---|---|
| **Interaction** | Text CLI (`--text`), voice input/output (microphone + TTS), local web UI with conversation log |
| **System tasks** | List/open macOS apps, open folders, web search, battery status, disk/OS info, workspace file listing |
| **Memory** | SQLite-backed notes and reminders with add, list, delete, and mark-done operations |
| **AI chat** | Optional general-purpose questions via OpenAI API or local Ollama server |
| **Status** | OS version, disk usage, Python version, current time |

## Architecture

```
User
  ├─ CLI (text mode)
  ├─ CLI (voice mode)
  └─ Web UI (browser)
        │
        ▼
  Assistant.handle(command)
        │
        ├─ Tools (built-in handlers)
        │    ├── status, help, capabilities
        │    ├── remember, notes, forget
        │    ├── remind, reminders, done
        │    └── chat (delegates to LLM)
        │
        ├─ System Tasks
        │    ├── list_apps, open_app
        │    ├── open_folder, search_web
        │    ├── current_time, battery_status
        │    └── list_workspace_files
        │
        ├─ Memory (SQLite)
        │    └── notes, reminders tables
        │
        └─ LLM Client
             ├── OpenAI (if OPENAI_API_KEY set)
             └── Ollama (if local server running)
```

### Module overview

| Module | Purpose |
|---|---|
| `assistant.py` | Entry point. Builds the `Assistant` instance, parses CLI args, runs the text or voice loop. |
| `tools.py` | Built-in command handlers. Maps text commands to memory and LLM operations. |
| `system_tasks.py` | System-level commands. Platform-aware handlers for apps, folders, battery, and file listing. |
| `llm.py` | LLM client. Routes to OpenAI or Ollama depending on configuration. No external framework dependency. |
| `memory.py` | SQLite store. Creates and manages `notes` and `reminders` tables. |
| `voice.py` | Audio I/O. pyttsx3 for TTS, speech_recognition for STT via Google Web Speech API. |
| `web.py` | Local HTTP server. Serves the web UI and exposes JSON API endpoints. |
| `config.py` | Configuration loader. Reads environment variables, constructs `Config` dataclass. |

## AI Architecture

Jervis supports two LLM providers, neither required for core functionality:

### OpenAI

When `OPENAI_API_KEY` is set, the `chat` command sends prompts to the OpenAI Responses API using the configured model. Requires the `openai` Python package (included in `requirements.txt`).

### Ollama

When no OpenAI key is set, Jervis checks for a local Ollama server at the configured URL (default `http://127.0.0.1:11434`). It probes `/api/tags` to confirm availability, then sends chat requests to `/api/chat`. Ollama must be running with a model pulled locally (e.g., `ollama pull llama3.2`).

### Fallback

If neither provider is available, the `chat` command returns a message explaining how to configure one. All system tasks, memory operations, and voice/text interaction work without any AI provider.

## Memory

Jervis stores persistent data in a SQLite database located at `.jarvis_data/memory.sqlite3` (relative to the working directory, or under the path set by `JARVIS_DATA_DIR`).

Two tables:

- **notes** — `id`, `body`, `created_at`
- **reminders** — `id`, `body`, `remind_at`, `created_at`, `done`

Reminders are stored with a time string but are not actively polled or delivered as notifications. They function as a persistent to-do list you can query and mark done.

## Platform Support

| Feature | macOS | Linux / Windows |
|---|---|---|
| Text CLI | Yes | Yes |
| Web UI | Yes | Yes |
| AI chat (OpenAI/Ollama) | Yes | Yes |
| Notes & reminders | Yes | Yes |
| Voice input/output | Yes (PyAudio needed) | Depends on audio drivers |
| Open apps by name | Yes | No — `open -a` is macOS-specific |
| Open folders in Finder | Yes | No — uses `open` command |
| Battery status | Yes (`pmset`) | No — macOS-specific |
| Web search | Yes | Yes (opens default browser) |

## Installation

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On macOS, voice input requires PyAudio:

```bash
brew install portaudio
pip install -r requirements.txt
```

## Configuration

All configuration is via environment variables:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | _(none)_ | Enables OpenAI chat when set |
| `JARVIS_OPENAI_MODEL` | `gpt-4.1-mini` | OpenAI model to use |
| `JARVIS_OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama server URL |
| `JARVIS_OLLAMA_MODEL` | `llama3.2` | Ollama model to use |
| `JARVIS_DATA_DIR` | `.jarvis_data` | Directory for the SQLite database |

Example:

```bash
export OPENAI_API_KEY="sk-..."
python -m jarvis
```

## Usage

### Web interface (default)

```bash
python -m jarvis.web
```

Opens `http://127.0.0.1:<port>` in your browser automatically.

### Text CLI

```bash
python -m jarvis --text
```

### Voice CLI

```bash
python -m jarvis
```

Requires microphone access and PyAudio. Falls back to text mode if voice is unavailable.

### Example commands

```
help
capabilities
open app Calculator
open folder ~/Downloads
search web for Python speech recognition
battery
remember my passport is in the blue drawer
notes
remind me to drink water at 18:30
reminders
forget 1
chat draft a short email asking for a meeting
status
exit
```

## Web Interface

The web server binds to `127.0.0.1` on a random port and opens automatically in the default browser.

### API endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Returns server, voice, and AI status |
| `POST` | `/api/command` | Send a text command, get a response |
| `POST` | `/api/listen` | Trigger microphone listening, returns transcribed command and response |
| `POST` | `/api/speak` | Send text to be spoken aloud (uses macOS `say` command) |
| `GET` | `/*` | Serves static files from `web/` |

The web UI provides a conversation view, quick-action buttons, a microphone button for voice input, and a waveform animation during listening. Sound output can be toggled on/off.

## Project Structure

```
jarvis/
  __init__.py        # Package version (0.1.0)
  __main__.py        # Module entrypoint
  assistant.py       # Assistant class, CLI loops, arg parsing
  config.py          # Config dataclass and env var loader
  llm.py             # OpenAI + Ollama client
  memory.py          # SQLite notes/reminders store
  system_tasks.py    # System command handlers (macOS-aware)
  tools.py           # Built-in tool handlers
  voice.py           # pyttsx3 speaker + speech_recognition listener
  web.py             # HTTP server and API handlers
web/
  index.html         # Web UI markup
  app.js             # Client-side JavaScript
  styles.css         # Styles
requirements.txt     # Python dependencies
run_llm_test.py      # Manual Ollama connectivity check
```

## Testing

There is no automated test suite. `run_llm_test.py` is a manual script for verifying Ollama connectivity.

## Security Considerations

- The web server binds to `127.0.0.1` only — it is not accessible from the network.
- There is no authentication. Anyone with local machine access can use the web interface.
- System task handlers use `subprocess.run` with fixed command arguments (e.g., `open -a`, `pmset`). No arbitrary shell commands are constructed from user input.
- Voice input is transcribed via the Google Web Speech API. Audio is sent to Google for recognition when voice mode is active.
- SQLite data is stored locally under `.jarvis_data/`.

## Limitations

- **macOS-specific system tasks** — App launching, folder opening, and battery status rely on macOS commands (`open`, `pmset`). These return platform-specific error messages on other operating systems.
- **Voice dependencies** — Requires PyAudio (system-level C library) and microphone access. Availability varies by platform and audio driver.
- **No active reminder delivery** — Reminders are stored and queryable but not pushed as notifications.
- **No authentication** — The local web interface has no login or access control.
- **LLM providers are optional** — Without OpenAI or Ollama configured, the `chat` command cannot answer general questions.
- **Voice transcription sends audio to Google** — The `speech_recognition` library uses Google's cloud API for speech-to-text.

## Roadmap

Reasonable next steps given the current project direction:

- Confirmation prompts for destructive or external actions (sending messages, deleting files)
- Calendar and email integrations
- Background reminder notifications
- Automated test suite
- Richer system automation (browser/desktop automation layer)

## License

No license has been selected yet. All rights reserved by default.
