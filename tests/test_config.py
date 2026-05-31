from pydantic import ValidationError

from app.core.config import Settings


def test_settings_accepts_secret_key_with_minimum_length():
    settings = Settings(
        DATABASE_URL="sqlite:///:memory:",
        SECRET_KEY="0123456789abcdef0123456789abcdef",
    )
    assert settings.SECRET_KEY == "0123456789abcdef0123456789abcdef"


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
    )
    assert settings.LOG_LEVEL == "DEBUG"
