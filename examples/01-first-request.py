"""
Пример 1: Первый запрос — проверка ключа через GET /me.

Запуск:
    pip install botix
    BOTIX_API_KEY=btx_live_... python 01-first-request.py
"""

import os
import sys

import botix


def main() -> int:
    api_key = os.environ.get("BOTIX_API_KEY")
    if not api_key:
        print("Не задана переменная окружения BOTIX_API_KEY", file=sys.stderr)
        return 1

    with botix.Client(api_key) as client:
        me = client.me()
        data = me.data
        print(f"Проект: {data.project_id}")
        print(f"Тариф: {data.plan_key}")
        print(f"Scopes: {', '.join(data.scopes or [])}")
        if data.rate_limit:
            rl = data.rate_limit
            print(f"Rate-limit: {rl.remaining}/{rl.limit} до {rl.reset_at}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
