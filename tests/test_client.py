"""Тесты инициализации Client."""

from __future__ import annotations

import pytest

import botix


def test_init_minimal() -> None:
    client = botix.Client("btx_live_test_key")
    assert client.api_client is not None
    assert client._config.access_token == "btx_live_test_key"
    assert client.auto_idempotency is True
    client.close()


def test_init_empty_key_raises() -> None:
    with pytest.raises(ValueError):
        botix.Client("")


def test_init_custom_host_and_options() -> None:
    client = botix.Client(
        "btx_live_test",
        host="http://localhost:8888",
        timeout=5.0,
        auto_idempotency=False,
        user_agent="MyApp/1.0",
    )
    assert client._config.host == "http://localhost:8888"
    assert client._timeout == 5.0
    assert client.auto_idempotency is False
    assert client.api_client.user_agent == "MyApp/1.0"
    client.close()


def test_authorization_header_uses_bearer_token() -> None:
    client = botix.Client("btx_live_abc123")
    auth = client._config.auth_settings()
    assert "bearerAuth" in auth
    assert auth["bearerAuth"]["value"] == "Bearer btx_live_abc123"
    client.close()


def test_resources_present() -> None:
    client = botix.Client("btx_live_test")
    for name in ("contacts", "messages", "scenarios", "chats", "channels", "webhooks"):
        assert hasattr(client, name), f"client.{name} resource missing"
    client.close()


def test_context_manager_closes() -> None:
    with botix.Client("btx_live_test") as client:
        assert client.api_client is not None
    # ApiClient.close() — должно работать идемпотентно, второй раз без падений.
    client.close()


def test_version_exported() -> None:
    assert botix.__version__ == "1.0.0"
