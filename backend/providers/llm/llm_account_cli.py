import os
import shutil
import subprocess
import tempfile

from .llm_provider import LLMProvider


def _transcript(messages):
    lines = []
    for message in messages:
        content = message.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                item.get("text", "") for item in content
                if isinstance(item, dict) and item.get("type") in {"input_text", "output_text", "text"}
            )
        lines.append(f"{message.get('role', 'user').upper()}: {content}")
    lines.append("ASSISTANT:")
    return "\n\n".join(lines)


class ClaudeAccountLLM(LLMProvider):
    """Use an existing official Claude Code browser sign-in."""

    def __init__(self, model_name="sonnet"):
        if not shutil.which("claude"):
            raise RuntimeError("Claude Code is not installed. Run scripts/connect_account.py claude")
        self.model_name = model_name or "sonnet"

    def generate(self, messages: list, image_b64: str | None = None) -> str:
        if image_b64:
            messages = [*messages, {"role": "system", "content": "A screen image was available but the account CLI adapter currently supports text only."}]
        with tempfile.TemporaryDirectory(prefix="riko-claude-") as workdir:
            result = subprocess.run(
                [
                    "claude", "-p", _transcript(messages), "--model", self.model_name,
                    "--output-format", "text", "--tools", "",
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=workdir,
                env={**os.environ, "ANTHROPIC_API_KEY": ""},
            )
        return result.stdout.strip()


class ChatGPTAccountLLM(LLMProvider):
    """Use an existing official Codex CLI ChatGPT OAuth sign-in."""

    def __init__(self, model_name="gpt-5.2-codex"):
        if not shutil.which("codex"):
            raise RuntimeError("OpenAI Codex CLI is not installed. Run scripts/connect_account.py chatgpt")
        self.model_name = model_name or "gpt-5.2-codex"

    def generate(self, messages: list, image_b64: str | None = None) -> str:
        output_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False) as output:
                output_path = output.name
            command = [
                "codex", "exec", "--skip-git-repo-check", "--sandbox", "read-only",
                "--output-last-message", output_path, "--model", self.model_name,
                _transcript(messages),
            ]
            with tempfile.TemporaryDirectory(prefix="riko-codex-") as workdir:
                subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=workdir,
                    env={**os.environ, "OPENAI_API_KEY": ""},
                )
            with open(output_path, encoding="utf-8") as output:
                return output.read().strip()
        finally:
            if output_path and os.path.exists(output_path):
                os.unlink(output_path)
