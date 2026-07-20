# 🌐 Deploying Riko as a Live Website

This guide covers taking Riko from `localhost`-only to a real domain over HTTPS, for **one user** (you) — not a multi-tenant setup. If you just want to run Riko locally, see the main [README](../README.md) instead.

---

## ⚠️ Read this before you deploy: the Vision feature will not work as expected

Riko's screen-vision feature (`backend/core/vision_manager.py`) calls `pyautogui.screenshot()` on **whatever machine is running the backend process**. On your own PC, that correctly captures your screen. Once the backend runs on a remote server, it captures *the server's* screen instead — which is either nonexistent (a headless VPS has no display) or, if it has one, definitely not what you're looking at.

This guide does not fix that. Fixing it properly means capturing the screen client-side (in the browser) and uploading it, which is a different, bigger feature than what exists today. Don't be surprised when `use_vision` does nothing useful post-deployment.

---

## Prerequisites

1. A domain name with a DNS `A` record pointing at your server's IP.
2. Docker + Docker Compose installed on that server.
3. GPT-SoVITS already set up and running somewhere reachable from your server (see the main README's TTS setup section). GPT-SoVITS is **not** part of this repo and is **not** deployed by anything in this guide — it stays an external service you run yourself.

---

## 1. Configure

```bash
cp .env.example .env
```

Fill in:
- `RIKO_API_KEY` — generate one with `openssl rand -hex 32`. Anything reachable from the public internet should have this set.
- `RIKO_ALLOWED_ORIGINS` — your domain (only matters if you deviate from the same-origin setup below).
- `SOVITS_URL` — see the networking section right below first, this isn't just "fill in a hostname."

Also put your real LLM provider API keys into `configs/character_config.yaml` (it's git-tracked with placeholder values — never commit real keys there).

## 2. GPT-SoVITS reachability (read this, it's not obvious)

Inside the `backend` container, `127.0.0.1` refers to the container itself, **not** the host machine. If GPT-SoVITS runs on the same physical server as the backend (the common case), the default `SOVITS_URL` (`http://127.0.0.1:9880/tts`) will silently fail to reach it once the backend is containerized. Pick one:

- **Simplest, if GPT-SoVITS is on the same host:** add `network_mode: host` to the `backend` service in `docker-compose.yml`. The default `SOVITS_URL` keeps working unmodified. Trade-off: `backend:8000` no longer resolves inside Compose's network, so also change the Caddyfile's `reverse_proxy backend:8000` lines to `reverse_proxy 127.0.0.1:8000`.
- **More portable, keeps container isolation:** leave the default bridge networking, add to the `backend` service:
  ```yaml
  extra_hosts:
    - "host.docker.internal:host-gateway"
  ```
  and set `SOVITS_URL=http://host.docker.internal:9880/tts` in `.env`.

## 3. Build the client

```bash
cd client
npm install
npm run build
```

This produces `client/dist/`, which `docker-compose.yml` mounts straight into the Caddy container. **You need to re-run this before every redeploy** — it's not built inside the Docker image.

## 4. Point the Caddyfile at your domain

Edit `Caddyfile`, replace `riko.example.com` with your real domain.

## 5. Run it

```bash
docker compose up -d --build
```

First run: Caddy automatically requests its Let's Encrypt certificate once your DNS resolves to this server — no manual certbot step.

## 6. Updating

```bash
git pull
cd client && npm run build && cd ..
docker compose up -d --build
```

---

## Troubleshooting

- **Every API call 500s / `/settings` fails right after startup:** `RikoCore.__init__` in `backend/api.py` swallows import errors during startup (logs and leaves `riko = None`). Check the backend container logs — if `chromadb`, `ollama`, `google-generativeai`, or `pyperclip` are missing, the `Dockerfile` here already installs them explicitly (they're absent from `requirements/*.txt`) — if you've modified the Dockerfile, make sure that install step is still there.
- **`docker build` fails compiling a package** (`pyopenjtalk`, `ctranslate2`, `llama-cpp-python` are the likely culprits): these compile native extensions. The Dockerfile installs `build-essential`, `cmake`, and `git` for this — if a build still fails, the error output will usually name the missing system library to add.
- **TTS requests time out or connection-refused:** almost always the GPT-SoVITS networking issue from step 2 above — double check `SOVITS_URL` actually resolves from *inside* the backend container (`docker compose exec backend curl -v $SOVITS_URL` or similar).
