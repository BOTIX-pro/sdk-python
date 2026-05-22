"""
Пример 3: Принять и верифицировать входящий webhook от BOTIX.

Минимальный Flask-приёмник. BOTIX подписывает webhook HMAC-SHA256 над сырым
телом запроса и кладёт результат в заголовок ``X-Botix-Signature``. Секрет
подписки выдан один раз при ``client.webhooks.create(url=..., events=[...])``.

Запуск:
    pip install botix flask
    BOTIX_WEBHOOK_SECRET=... python 03-verify-webhook.py

Затем подписку BOTIX направьте на ``http://your-host:5000/botix-webhook``.
"""

import os
import sys

import botix


def main() -> int:
    secret = os.environ.get("BOTIX_WEBHOOK_SECRET")
    if not secret:
        print("Не задана переменная BOTIX_WEBHOOK_SECRET", file=sys.stderr)
        return 1

    try:
        from flask import Flask, abort, request
    except ImportError:
        print("Установите flask: pip install flask", file=sys.stderr)
        return 1

    app = Flask(__name__)

    @app.route("/botix-webhook", methods=["POST"])
    def handler():
        raw_body = request.get_data()  # сырое тело — обязательно
        signature = request.headers.get("X-Botix-Signature", "")
        event_name = request.headers.get("X-Botix-Event", "")
        request_id = request.headers.get("X-Botix-Request-Id", "")

        if not botix.verify_webhook(raw_body, signature, secret):
            abort(401, "Invalid signature")

        event = request.get_json(silent=True) or {}
        print(f"[{request_id}] {event_name}: {event.get('data')}")
        return "", 200

    app.run(host="0.0.0.0", port=5000)
    return 0


if __name__ == "__main__":
    sys.exit(main())
