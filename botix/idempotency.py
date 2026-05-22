"""
Хелперы Idempotency-Key и обёртка ответа.

BOTIX поддерживает заголовок ``Idempotency-Key`` (стандарт Stripe) на мутирующих
эндпоинтах (`POST /messages`, `POST /scenarios/{id}/run`). Повторный запрос с
тем же ключом в течение 24 часов возвращает сохранённый ответ + заголовок
``Idempotent-Replayed: 1``.

SDK генерирует ключ автоматически, если разработчик не передал свой.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


def generate_idempotency_key() -> str:
    """Сгенерировать UUID v4 как Idempotency-Key."""
    return str(uuid.uuid4())


@dataclass
class Response:
    """Обёртка над ответом мутирующих методов SDK.

    Атрибуты:
        data — десериализованное тело ответа (типизированная pydantic-модель).
        replayed — True, если BOTIX вернул заголовок ``Idempotent-Replayed: 1``
                   (значит ответ из кеша по совпадению Idempotency-Key, не свежий).
        request_id — UUID v4 из заголовка ``X-Request-Id`` (если был).
        status_code — HTTP-код ответа.
        headers — все заголовки ответа (lowercased keys).
    """

    data: Any
    replayed: bool = False
    request_id: Optional[str] = None
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, api_response: Any) -> "Response":
        """Собрать обёртку из ApiResponse[T] сгенерированного клиента."""
        headers: Mapping[str, str] = api_response.headers or {}
        # urllib3 возвращает HTTPHeaderDict — case-insensitive lookup.
        lower = {str(k).lower(): str(v) for k, v in headers.items()}
        replayed = lower.get("idempotent-replayed", "") == "1"
        return cls(
            data=api_response.data,
            replayed=replayed,
            request_id=lower.get("x-request-id"),
            status_code=int(api_response.status_code),
            headers=lower,
        )
