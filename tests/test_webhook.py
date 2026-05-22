"""Тесты verify_webhook — корректность HMAC, timing-safe, граничные кейсы."""

from __future__ import annotations

import hashlib
import hmac

import botix


SECRET = "wh_secret_aabbcc"


def _sign(payload: bytes, secret: str = SECRET) -> str:
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def test_valid_signature_bytes_payload() -> None:
    body = b'{"event":"contact.created","data":{"id":42}}'
    sig = _sign(body)
    assert botix.verify_webhook(body, sig, SECRET) is True


def test_valid_signature_str_payload() -> None:
    body = '{"event":"contact.created","data":{"id":42}}'
    sig = _sign(body.encode("utf-8"))
    assert botix.verify_webhook(body, sig, SECRET) is True


def test_wrong_signature() -> None:
    body = b'{"event":"contact.created"}'
    assert botix.verify_webhook(body, "deadbeef", SECRET) is False


def test_wrong_secret() -> None:
    body = b'{"event":"contact.created"}'
    sig = _sign(body, "other_secret")
    assert botix.verify_webhook(body, sig, SECRET) is False


def test_modified_payload_invalidates_signature() -> None:
    body = b'{"event":"contact.created"}'
    sig = _sign(body)
    tampered = b'{"event":"contact.deleted"}'
    assert botix.verify_webhook(tampered, sig, SECRET) is False


def test_empty_signature_returns_false() -> None:
    assert botix.verify_webhook(b"anything", "", SECRET) is False


def test_empty_secret_returns_false() -> None:
    assert botix.verify_webhook(b"anything", "deadbeef", "") is False


def test_signature_with_whitespace_is_trimmed() -> None:
    body = b"payload"
    sig = _sign(body)
    assert botix.verify_webhook(body, f"  {sig}  \n", SECRET) is True


def test_uses_constant_time_compare() -> None:
    # Не настоящий timing-тест — просто проверка, что не падает на разных длинах
    # (compare_digest сам по себе обрабатывает разные длины без раннего возврата).
    body = b"x"
    sig = _sign(body)
    short_wrong = "00"
    long_wrong = "0" * 200
    assert botix.verify_webhook(body, short_wrong, SECRET) is False
    assert botix.verify_webhook(body, long_wrong, SECRET) is False
    assert botix.verify_webhook(body, sig, SECRET) is True
