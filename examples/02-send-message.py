"""
Пример 2: Отправить сообщение через канал.

В качестве канала будет выбран явно переданный (telegram) или, если не задан, —
last_channel контакта. SDK автоматически добавит Idempotency-Key (UUID v4).

Запуск:
    pip install botix
    BOTIX_API_KEY=btx_live_... CONTACT_ID=42 python 02-send-message.py
"""

import os
import sys

import botix


def main() -> int:
    api_key = os.environ.get("BOTIX_API_KEY")
    contact_id = os.environ.get("CONTACT_ID")
    if not api_key or not contact_id:
        print("Нужны переменные BOTIX_API_KEY и CONTACT_ID", file=sys.stderr)
        return 1

    with botix.Client(api_key) as client:
        response = client.messages.send(
            contact_id=int(contact_id),
            content="Привет! Это тестовое сообщение из BOTIX SDK для Python.",
            channel="telegram",
        )

    print(f"Сообщение отправлено: id={response.data.id}, status={response.data.status}")
    if response.replayed:
        print("(ответ из кеша — этот Idempotency-Key уже отправлял сервер)")
    if response.request_id:
        print(f"X-Request-Id: {response.request_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
