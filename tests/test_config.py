from types import SimpleNamespace

from pydantic import ValidationError

from app.core.config import Settings
from app.core.rate_limit import get_client_ip


def test_settings_accepts_secret_key_with_minimum_length():
    settings = Settings(
        DATABASE_URL="sqlite:///:memory:",
        SECRET_KEY="0123456789abcdef0123456789abcdef",
    )
    assert settings.SECRET_KEY == "0123456789abcdef0123456789abcdef"
    assert settings.SQL_ECHO is False
    assert settings.TRUST_PROXY_HEADERS is False


def test_settings_rejects_short_secret_key():
    try:
        Settings(
            DATABASE_URL="sqlite:///:memory:",
            SECRET_KEY="short-secret-key",
        )
    except ValidationError as exc:
        assert "SECRET_KEY must be at least 32 bytes for HS256" in str(exc)
    else:
        raise AssertionError("Expected short SECRET_KEY to raise ValidationError")


def test_settings_normalizes_log_level():
    settings = Settings(
        DATABASE_URL="sqlite:///:memory:",
        SECRET_KEY="0123456789abcdef0123456789abcdef",
        LOG_LEVEL="debug",
        SQL_ECHO=True,
        TRUST_PROXY_HEADERS=True,
    )
    assert settings.LOG_LEVEL == "DEBUG"
    assert settings.SQL_ECHO is True
    assert settings.TRUST_PROXY_HEADERS is True


def test_get_client_ip_ignores_forwarded_header_by_default(monkeypatch):
    monkeypatch.setattr("app.core.rate_limit.settings.TRUST_PROXY_HEADERS", False)
    request = SimpleNamespace(
        client=SimpleNamespace(host="127.0.0.1"),
        headers={"X-Forwarded-For": "203.0.113.10"},
    )

    assert get_client_ip(request) == "127.0.0.1"


def test_get_client_ip_uses_forwarded_header_when_enabled(monkeypatch):
    monkeypatch.setattr("app.core.rate_limit.settings.TRUST_PROXY_HEADERS", True)
    request = SimpleNamespace(
        client=SimpleNamespace(host="127.0.0.1"),
        headers={"X-Forwarded-For": "203.0.113.10, 10.0.0.1"},
    )

    assert get_client_ip(request) == "203.0.113.10"
