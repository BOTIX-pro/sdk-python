"""Тесты Idempotency-Key и обёртки Response."""

from __future__ import annotations

import re
import uuid

import botix
from botix.idempotency import Response, generate_idempotency_key


UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def test_generate_idempotency_key_is_uuid4() -> None:
    key = generate_idempotency_key()
    assert UUID4_RE.match(key), f"not a UUID v4: {key}"
    # На всякий случай — uuid.UUID() обязан принять без ошибки и быть version=4.
    parsed = uuid.UUID(key)
    assert parsed.version == 4


def test_generate_idempotency_key_uniqueness() -> None:
    keys = {generate_idempotency_key() for _ in range(1000)}
    assert len(keys) == 1000


def test_response_dataclass_defaults() -> None:
    r = Response(data={"id": 1})
    assert r.data == {"id": 1}
    assert r.replayed is False
    assert r.request_id is None
    assert r.status_code == 200
    assert r.headers == {}


def test_response_from_api_response_detects_replayed() -> None:
    class FakeApiResponse:
        status_code = 200
        headers = {
            "Idempotent-Replayed": "1",
            "X-Request-Id": "req-abc-123",
            "Content-Type": "application/json",
        }
        data = {"id": 7}
        raw_data = b"{}"

    r = Response.from_api_response(FakeApiResponse())
    assert r.replayed is True
    assert r.request_id == "req-abc-123"
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/json"
    assert r.data == {"id": 7}


def test_response_from_api_response_no_replay() -> None:
    class FakeApiResponse:
        status_code = 201
        headers = {"Content-Type": "application/json"}
        data = {"id": 7}
        raw_data = b"{}"

    r = Response.from_api_response(FakeApiResponse())
    assert r.replayed is False
    assert r.status_code == 201


def test_auto_idempotency_can_be_disabled() -> None:
    client = botix.Client("btx_live_test", auto_idempotency=False)
    assert client.auto_idempotency is False
    client.close()


def test_auto_idempotency_default_is_true() -> None:
    client = botix.Client("btx_live_test")
    assert client.auto_idempotency is True
    client.close()
