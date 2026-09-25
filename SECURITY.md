# Security Policy

## Supported Versions

Security fixes are applied to the latest code on the `main` branch. There are no tagged releases; always use the most recent commit of `main`.

## Reporting a Vulnerability

Please do **not** open a public GitHub issue for an exploitable vulnerability.

Report it privately using GitHub's vulnerability reporting for this repository:

1. Open the repository on GitHub → **Security** tab → **Report a vulnerability**.
2. Include a description, reproduction steps, and the potential impact.

If the private reporting form is not available on this repository, open a normal issue asking to establish a private channel first, without including exploit details.

> Note: this project does not have a dedicated security email. GitHub's private vulnerability reporting is the supported channel.

## Scope

Jervis is a **local personal assistant** — there is no hosted service.

**In scope**

- The local web server (`jarvis/web.py`): request handling, path traversal, binding beyond `127.0.0.1`
- Command handling (`jarvis/tools.py`, `jarvis/system_tasks.py`): injection via commands such as `open app` or `search web`
- Handling of `OPENAI_API_KEY` and other environment configuration (`jarvis/config.py`)
- SQLite data safety in `jarvis/memory.py`
- Secrets or credentials committed to the repository

**Out of scope**

- Vulnerabilities in third-party dependencies (report upstream)
- The upstream OpenAI, Ollama, and Google Web Speech APIs
- Physical access attacks on the machine Jervis runs on

## Security Practices for Contributors

- Never commit `.env` or real API keys — only placeholders in `.env.example`.
- Keep the web server bound to `127.0.0.1`; do not add network exposure without authentication.
- System task handlers must keep using fixed argument lists with `subprocess.run` — never build shell strings from user input.
- User input must not be passed unsanitized to shell or file-system operations.
