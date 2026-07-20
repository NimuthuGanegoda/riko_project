# 🌐 Deploying Riko for Free on Render

Free-tier alternative to [DEPLOYMENT.md](DEPLOYMENT.md). No VPS, no domain purchase, no Caddy — Render hosts the backend and client as two separate free services. Read the caveats section before you start; a free instance is a real constraint, not just "the same thing but cheaper."

---

## ⚠️ Read this first

- **Vision doesn't work here either** — same reason as the VPS guide: `pyautogui.screenshot()` captures whatever machine runs the backend, which on Render is a headless container with no screen. See [DEPLOYMENT.md's vision section](DEPLOYMENT.md#-read-this-before-you-deploy-the-vision-feature-will-not-work-as-expected) for the full explanation.
- **512MB RAM, 0.1 CPU on the free plan.** Local ASR (Whisper) and local LLM (llama.cpp/Ollama) will not fit. This guide assumes a cloud LLM provider (`gemini` or `openai` in `character_config.yaml`, both lazy-imported so the heavy local-inference libraries never load) and `asr_enabled: false` (browser speech recognition instead of server-side Whisper).
- **Free web services spin down after 15 minutes idle** and take about a minute to wake back up on the next request. First message after idle time will hang, not fail — that's expected.
- **Ephemeral filesystem.** Anything written at runtime (generated TTS `.wav` files, `chat_history.json`) is wiped on every restart/redeploy/spin-down. Fine for this app — nothing in the request path depends on that state surviving.
- **GPT-SoVITS (TTS) is still not deployed by this guide**, same as the VPS path. Unless you expose your own GPT-SoVITS instance to the public internet and point `SOVITS_URL` at it, TTS calls will fail — the backend already catches that (`sovits_gen` failures in `/chat` and `/voice` are wrapped in try/except and just return `audio_url: null`), so the app stays usable text-only rather than 500ing.

---

## Overview

Two Render services, both free:

| Service | Type | Source |
|---|---|---|
| Backend | Web Service (Docker) | repo root `Dockerfile` |
| Client | Static Site | `client/` (Vite build) |

They talk to each other over CORS (`RIKO_ALLOWED_ORIGINS` on the backend, `VITE_API_BASE` baked into the client at build time) — no reverse proxy needed, so the Caddyfile/`docker-compose.yml` from the VPS guide are unused here.

---

## 1. Real API keys without committing them

`configs/character_config.yaml` is git-tracked with placeholder keys (`sk-...`, `YOUR_GEMINI_API_KEY`) — those load straight from the YAML file (`RikoCore` reads `self.config.get('OPENAI_API_KEY')` / `GEMINI_API_KEY`, there's no env-var fallback), and the `Dockerfile` deliberately does **not** bake `configs/` into the image, so you can't just edit the file and commit it.

Use Render's **Secret Files** on the backend service instead:

1. Copy `configs/character_config.yaml` locally and fill in your real `GEMINI_API_KEY` (or `OPENAI_API_KEY`).
2. In it, also set `asr_enabled: false` (see caveats above).
3. In the Render dashboard, on the backend service: **Environment → Secret Files → Add Secret File**, filename `/app/configs/character_config.yaml`, paste the contents.

Render mounts it at that exact path at runtime, overriding what's (not) in the image — matches where `backend/api.py` looks for it (`CONFIG_PATH` resolves to `/app/configs/character_config.yaml` given the Dockerfile's `WORKDIR /app/backend`).

## 2. Create the backend Web Service

New → Web Service → connect this repo → Environment: **Docker** (uses the root `Dockerfile` as-is).

Environment variables:
- `RIKO_ALLOWED_ORIGINS` — set after step 3 once you know the static site's URL (e.g. `https://riko-client.onrender.com`).
- `RIKO_API_KEY` — generate with `openssl rand -hex 32`, recommended since this is public.
- `SOVITS_URL` — only if you have a publicly-reachable GPT-SoVITS instance; otherwise leave it and TTS just no-ops (see caveats).

`RIKO_HOST=0.0.0.0` and the `$PORT` binding are already handled — `Dockerfile` sets the former, `backend/api.py` reads `PORT` from the environment (Render sets it automatically).

Deploy, then note the service URL (`https://<something>.onrender.com`).

## 3. Create the client Static Site

New → Static Site → same repo.

- **Root directory:** `client`
- **Build command:** `npm install && npm run build`
- **Publish directory:** `dist`
- **Environment variable:** `VITE_API_BASE` = the backend URL from step 2 (e.g. `https://riko-backend.onrender.com`). This is read at build time (`client/src/App.tsx`), so changing it requires a rebuild, not just a restart.

Deploy, then go back to the backend service and set `RIKO_ALLOWED_ORIGINS` to this static site's URL, and redeploy the backend so CORS picks it up.

## 4. Verify

Open the static site URL. `/settings` should load the configured provider/model. Send a chat message — expect a ~1 minute delay on the very first request if the backend had spun down.

## 5. Updating

Render auto-deploys both services on push to the connected branch by default. No manual `npm run build` step like the VPS guide — Render runs the build command itself on every deploy.

---

## Troubleshooting

- **CORS errors in the browser console:** `RIKO_ALLOWED_ORIGINS` on the backend doesn't match the static site's actual URL, or the backend wasn't redeployed after setting it.
- **`/settings` 500s / everything 500s:** same underlying cause as the VPS guide — check the backend's Render logs for the real startup error (`RikoCore.__init__` swallows it and leaves `riko = None`). Almost always a missing secret file or a bad key in it.
- **Build fails or times out:** the free plan gives 500 build minutes/month; this image is large (torch, transformers, funasr, etc., for the optional local-inference paths) and can be slow to build. If it fails outright, check Render's build logs for the actual error — it's usually a specific package failing to compile, same culprits as the VPS guide (`pyopenjtalk`, `ctranslate2`, `llama-cpp-python`).
- **First request after idle takes ~1 minute:** expected free-tier spin-down behavior, not a bug.
