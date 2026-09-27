#!/usr/bin/env python3
"""Launch an official provider login flow in the user's default browser."""

import argparse
import shutil
import subprocess
import sys


PROVIDERS = {
    "google": {
        "executable": "gcloud",
        "command": ["gcloud", "auth", "application-default", "login"],
        "install": "Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install",
        "provider": "google_account",
    },
    "chatgpt": {
        "executable": "codex",
        "command": ["codex", "login"],
        "install": "Install OpenAI Codex CLI: npm install -g @openai/codex",
        "provider": "chatgpt_account",
    },
    "claude": {
        "executable": "claude",
        "command": ["claude", "auth", "login"],
        "install": "Install Claude Code: https://docs.anthropic.com/en/docs/claude-code/setup",
        "provider": "claude_account",
    },
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider", choices=PROVIDERS)
    args = parser.parse_args()
    details = PROVIDERS[args.provider]

    if not shutil.which(details["executable"]):
        print(details["install"], file=sys.stderr)
        return 2

    print(f"Starting the official {args.provider} sign-in. Your default browser should open automatically.")
    print("Complete sign-in in the browser, then return to this terminal.")
    result = subprocess.run(details["command"])
    if result.returncode == 0:
        print(f"\nConnected. Select '{details['provider']}' in Riko's provider menu.")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
