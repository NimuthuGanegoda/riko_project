# AIRI + Riko integration

This project can use [Project AIRI](https://github.com/moeru-ai/airi) as its advanced character UI while retaining Riko's Python model routing, memory, facts, actions, and vision backend.

This is intentionally an API-level combination rather than a direct source-tree copy. AIRI is a large pnpm monorepo with a different Vue architecture; copying its files into Riko's React client would create two conflicting build systems and make updates difficult.

## Architecture

```text
AIRI stage (VRM/Live2D, voice, UI)
              |
              | OpenAI-compatible HTTP API
              v
Riko FastAPI (/v1/chat/completions, /v1/models)
              |
              +-- Riko personality and history
              +-- memory and fact extraction
              +-- actions and optional vision
              +-- configured local/cloud LLM
```

## Run

1. Start Riko's backend:

   ```bash
   ./run_web.sh
   ```

   The API defaults to `http://127.0.0.1:8000`.

2. Clone and start AIRI separately (Node and pnpm versions should follow AIRI's current documentation):

   ```bash
   git clone https://github.com/moeru-ai/airi.git
   cd airi
   pnpm install
   pnpm dev
   ```

3. In AIRI's onboarding or provider settings select **OpenAI Compatible** and use:

   - Base URL: `http://127.0.0.1:8000/v1`
   - API key: any non-empty value when `RIKO_API_KEY` is unset
   - Model: use the model returned by `GET http://127.0.0.1:8000/v1/models`

   If `RIKO_API_KEY` is set, enter that exact value as AIRI's API key. Riko accepts it as a Bearer token for OpenAI compatibility.

## Remote or container use

Set `RIKO_ALLOWED_ORIGINS` to AIRI's public origin and put both applications behind HTTPS. Browser microphone access and many browser APIs require HTTPS outside localhost.

Do not expose Riko publicly without setting `RIKO_API_KEY`.

## Supported compatibility API

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
  - regular JSON completions
  - server-sent-event streaming
  - plain text and OpenAI structured text message content

AIRI owns avatar rendering and its own speech pipeline. Riko's original `/chat`, `/voice`, `/audio`, and `/settings` APIs remain available to the bundled React client.

## Attribution

Project AIRI is copyright its contributors and distributed under the MIT License. No AIRI source is vendored by this integration; AIRI runs as an independently installed frontend and communicates through its documented OpenAI-compatible provider interface.
