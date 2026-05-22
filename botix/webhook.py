"""
Проверка подписи webhook-сообщений от BOTIX.

BOTIX подписывает каждое webhook-сообщение HMAC-SHA256 над сырым телом запроса
и кладёт результат в заголовок `X-Botix-Signature`. Секрет — поле `secret`,
выданное при создании подписки (показывается один раз).
"""

from __future__ import annotations

import hmac
from hashlib import sha256
from typing import Union


def verify_webhook(
    raw_payload: Union[bytes, str],
    signature_header: str,
    secret: str,
) -> bool:
    """Сверить HMAC-подпись webhook-сообщения от BOTIX.

    :param raw_payload: сырое тело HTTP-запроса (как пришло, без парсинга JSON)
    :param signature_header: значение заголовка ``X-Botix-Signature``
    :param secret: секрет подписки, выданный BOTIX при ``POST /webhooks``
    :return: True если подпись валидна, иначе False

    Сравнение через ``hmac.compare_digest`` — устойчиво к timing-атакам.
    """
    if not signature_header or not secret:
        return False

    if isinstance(raw_payload, str):
        body = raw_payload.encode("utf-8")
    else:
        body = raw_payload

    expected = hmac.new(secret.encode("utf-8"), body, sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header.strip())
