# Contributing to Project Riko

This is a small, mostly solo project — this doc is intentionally short.

## Running it locally

See the [README](README.md) for the full setup/install guide (backend, client, hardware detection, GPT-SoVITS).

## Running tests

```bash
pip install pytest pillow
pytest tests/
```

The suite covers `backend/managers/action_manager.py`, `backend/managers/fact_manager.py`, and `backend/core/vision_manager.py` — the pieces most exposed to untrusted input (LLM output, user text). It does not require GPU, models, or API keys.

For the client:

```bash
cd client
nvm use          # Node 20+ required, see client/.nvmrc
npm install
npx tsc --noEmit
npm run build
```

## Before opening a PR

- Run the tests above and make sure they pass.
- Keep changes scoped — this repo has a history of half-finished features shipping as if they were complete (see `docs/DEPLOYMENT.md` and past audits); if you're adding a feature, wire it end to end or clearly flag what's a stub.
- If you touch `backend/managers/action_manager.py` or anything that executes LLM-decided actions, keep the allowlist/validation pattern already there — don't reintroduce passing LLM output straight to a shell.
