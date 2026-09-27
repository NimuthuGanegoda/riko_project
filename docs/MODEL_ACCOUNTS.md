# Connecting model providers

Riko supports Google Gemini, OpenAI, Anthropic Claude, Ollama, and local models.

## Important account limitation

A consumer account login is not the same as third-party API authorization:

- A ChatGPT Free/Plus/Pro subscription does not grant OpenAI API usage. Create an API key and configure API billing at `platform.openai.com`.
- A Claude consumer subscription should not be copied, scraped, or unofficially authenticated by Riko. Use an Anthropic API key from the Anthropic Console.
- Google is the exception supported here: Gemini can use a Gemini API key, or local Google Application Default Credentials (ADC). Google AI subscription benefits do not necessarily include Gemini API billing/quota.

Riko deliberately does not ask for Google, ChatGPT, or Claude passwords and does not store browser session cookies. This avoids credential theft risks and provider terms-of-service problems.

## Configuration

Copy `.env.example` to `.env`, then set one or more credentials:

```dotenv
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

Environment variables override values in `configs/character_config.yaml`. Restart the backend after changing credentials. Never commit `.env`.

Select `openai`, `anthropic`, or `gemini` from Riko's provider selector. If no model is supplied, Riko uses a suitable default for that provider.

## Browser login without API keys (local installation)

Riko includes a launcher for the providers' official authentication tools. Each command opens your default web browser automatically:

```bash
python scripts/connect_account.py google
python scripts/connect_account.py chatgpt
python scripts/connect_account.py claude
```

Then select `google_account`, `chatgpt_account`, or `claude_account` in Riko. These modes intentionally use the official installed CLI and its protected credential cache; Riko never receives your password or copies browser cookies.

Prerequisites:

- Google: install Google Cloud CLI. The launcher runs `gcloud auth application-default login`.
- ChatGPT: install Codex CLI with `npm install -g @openai/codex`. The launcher runs `codex login` and uses subscription access available to that CLI.
- Claude: install Claude Code. The launcher runs `claude auth login`; a supported paid Claude/Console account is required.

The backend must run as the same operating-system user that completed login. Account-backed CLI calls can be slower than direct APIs and the provider controls available models and subscription limits.

For remote/Docker deployments, a browser opened by the server would be on the wrong machine and interactive callbacks may be unreachable. Complete login on the host and deliberately mount the provider credential store, or use workload identity/API credentials. Never expose a generic web endpoint that can run login commands.

Google ADC may require a Google Cloud project with the relevant API and billing/quota configured. For production servers, prefer a narrowly scoped workload identity or service account.

## Local and free option

Install Ollama, pull a supported model, and select `ollama`. This requires no cloud account or API key:

```bash
ollama pull llama3
```

## Security

Provider credentials remain server-side. They are never returned by `/settings` and should not be entered into the browser client. When exposing Riko over a network, set `RIKO_API_KEY` as a separate access secret.
