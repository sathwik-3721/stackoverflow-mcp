"""Unit tests for configuration loading."""

from stackoverflow_mcp.config import Settings


def test_default_config_settings():
    s = Settings()
    assert s.STACKEXCHANGE_KEY is None
    assert s.STACKOVERFLOW_MAX_RESULTS == 10
    assert s.STACKOVERFLOW_API_TIMEOUT_SECONDS == 15
    assert s.STACKOVERFLOW_API_MAX_RETRIES == 3
    assert s.STACKOVERFLOW_LOG_LEVEL == "INFO"


def test_env_override(monkeypatch):
    monkeypatch.setenv("STACKEXCHANGE_KEY", "test_key_123")
    monkeypatch.setenv("STACKOVERFLOW_MAX_RESULTS", "5")

    s = Settings()
    assert s.STACKEXCHANGE_KEY == "test_key_123"
    assert s.STACKOVERFLOW_MAX_RESULTS == 5
