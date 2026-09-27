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

## Google account login (local installation)

To use your Google account without a Gemini API key, install the Google Cloud CLI and run:

```bash
gcloud auth application-default login
```

Then leave `GEMINI_API_KEY` empty and start Riko from the same user account. ADC may require a Google Cloud project with the relevant API and billing/quota configured.

For server deployments, use a narrowly scoped workload identity or service account. Do not upload your personal ADC file through the web UI.

## Local and free option

Install Ollama, pull a supported model, and select `ollama`. This requires no cloud account or API key:

```bash
ollama pull llama3
```

## Security

Provider credentials remain server-side. They are never returned by `/settings` and should not be entered into the browser client. When exposing Riko over a network, set `RIKO_API_KEY` as a separate access secret.
