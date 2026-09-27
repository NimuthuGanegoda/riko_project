import os


def provider_api_key(provider, config):
    """Return a cloud provider key, preferring environment configuration."""
    variable = {
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }.get(provider)
    if not variable:
        return None
    value = os.environ.get(variable) or config.get(variable)
    if isinstance(value, str) and (not value.strip() or "YOUR_" in value or value == "sk-..."):
        return None
    return value
