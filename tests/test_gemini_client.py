import pytest

from gemini_client import get_api_key


def test_get_api_key_reads_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    assert get_api_key() == "test-key"


def test_get_api_key_missing_raises(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        get_api_key()
