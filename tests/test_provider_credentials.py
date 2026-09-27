from backend.providers.llm.credentials import provider_api_key


def test_provider_key_prefers_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "from-environment")

    assert provider_api_key("openai", {"OPENAI_API_KEY": "from-config"}) == "from-environment"


def test_placeholder_key_is_not_used(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    assert provider_api_key("anthropic", {"ANTHROPIC_API_KEY": "YOUR_ANTHROPIC_API_KEY"}) is None


def test_local_provider_does_not_receive_cloud_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "secret")

    assert provider_api_key("ollama", {}) is None
