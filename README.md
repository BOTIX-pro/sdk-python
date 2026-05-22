# BOTIX SDK для Python

Официальная клиентская библиотека для публичного API BOTIX — платформы визуального конструктора чат-ботов и AI-ассистентов.

[![PyPI version](https://img.shields.io/pypi/v/botix.svg)](https://pypi.org/project/botix/)
[![Python versions](https://img.shields.io/pypi/pyversions/botix.svg)](https://pypi.org/project/botix/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/BOTIX-pro/sdk-python/actions/workflows/test.yml/badge.svg)](https://github.com/BOTIX-pro/sdk-python/actions/workflows/test.yml)

## Что это

BOTIX — облачная SaaS-платформа визуального конструктора чат-ботов: Telegram, WhatsApp, ВКонтакте, виджет на сайте. SDK даёт типизированный доступ к публичному REST API BOTIX из Python-приложений: контакты, сообщения, сценарии, чаты, webhooks.

## Установка

```bash
pip install botix
```

Минимальная версия Python — 3.9.

## Первый запрос

Получите API-ключ в кабинете BOTIX: «Настройки → API-ключи → Создать ключ». Ключ показывается один раз — сохраните его.

```python
import botix

client = botix.Client("btx_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

me = client.me()
print(me.data.project_id, me.data.scopes, me.data.plan_key)
```

Возвращается контекст текущего ключа: ID проекта, разрешённые scopes, тариф клиента и остаток rate-limit.

## Отправка сообщения

```python
response = client.messages.send(
    contact_id=42,
    content="Привет! Это сообщение из BOTIX SDK.",
    channel="telegram",  # опционально — иначе берётся last_channel контакта
)
print(response.data.id, response.data.status)
if response.replayed:
    print("Сервер вернул кешированный ответ по совпадению Idempotency-Key")
```

SDK автоматически генерирует `Idempotency-Key` (UUID v4) для защиты от случайных дублей при сетевых сбоях. Чтобы отключить: `botix.Client(api_key, auto_idempotency=False)`. Свой ключ — `client.messages.send(..., idempotency_key="my-uuid")`.

## Webhooks: проверка подписи

BOTIX подписывает каждое входящее webhook-сообщение HMAC-SHA256 над сырым телом запроса. Секрет вы получили один раз при создании подписки через `client.webhooks.create(...)`.

```python
from flask import Flask, request, abort
import botix

app = Flask(__name__)
WEBHOOK_SECRET = "ваш_секрет_подписки"

@app.route("/botix-webhook", methods=["POST"])
def botix_webhook():
    raw_body = request.get_data()  # ВАЖНО: сырое тело, не request.json
    signature = request.headers.get("X-Botix-Signature", "")

    if not botix.verify_webhook(raw_body, signature, WEBHOOK_SECRET):
        abort(401, "Invalid signature")

    event = request.json
    print(event["event"], event["data"])
    return "", 200
```

## Работа с ошибками

SDK кидает `botix.ApiException` на любой не-2xx ответ. Код ошибки BOTIX лежит в теле ответа.

```python
import botix
import json

client = botix.Client("btx_live_...")

try:
    contact = client.contacts.get(99999)
except botix.ApiException as e:
    body = json.loads(e.body) if e.body else {}
    code = body.get("error", {}).get("code")
    print(f"HTTP {e.status} / {code}: {body.get('error', {}).get('message')}")
```

Возможные коды (полный список — в [документации API](https://developers.botix.pro)):

| Код | HTTP | Когда |
|---|---|---|
| `MISSING_API_KEY` | 401 | Нет заголовка Authorization |
| `INVALID_API_KEY` | 401 | Ключ не существует или подделан |
| `KEY_REVOKED` | 401 | Ключ отозван |
| `INSUFFICIENT_SCOPE` | 403 | У ключа нет нужного scope |
| `API_NOT_AVAILABLE_ON_PLAN` | 403 | Тариф клиента не включает API |
| `TRIAL_READ_ONLY` | 403 | Триал — мутирующие методы запрещены |
| `RATE_LIMIT_EXCEEDED` | 429 | Превышен per-minute или per-day лимит |
| `NO_CHANNEL_AVAILABLE` | 422 | Не удалось определить канал отправки |
| `CHANNEL_NOT_SUPPORTED_YET` | 422 | Канал ещё не подключён к API |
| `CONTACT_NOT_REACHABLE` | 422 | У контакта нет chat_id/phone для канала |
| `DELIVERY_FAILED` | 502 | Канал отверг отправку |

## Доступные ресурсы

```python
client.me()                                        # GET  /me
client.contacts.list(page=1, per_page=50, ...)     # GET  /contacts
client.contacts.get(id)                            # GET  /contacts/{id}
client.contacts.create(**fields)                   # POST /contacts
client.contacts.update(id, **fields)               # PUT  /contacts/{id}
client.contacts.delete(id)                         # DELETE /contacts/{id}
client.contacts.add_tag(id, tag)                   # POST /contacts/{id}/tags
client.contacts.remove_tag(id, tag)                # DELETE /contacts/{id}/tags/{tag}

client.messages.list(...)                          # GET  /messages
client.messages.send(contact_id, content, ...)     # POST /messages

client.scenarios.list()                            # GET  /scenarios
client.scenarios.run(id, contact_id, ...)          # POST /scenarios/{id}/run

client.chats.list(...)                             # GET  /chats
client.chats.messages(chat_id)                     # GET  /chats/{id}/messages

client.channels.list()                             # GET  /channels

client.webhooks.list()                             # GET  /webhooks
client.webhooks.create(url, events)                # POST /webhooks
client.webhooks.update(id, ...)                    # PUT  /webhooks/{id}
client.webhooks.delete(id)                         # DELETE /webhooks/{id}
client.webhooks.test(id)                           # POST /webhooks/{id}/test
```

Примеры в [examples/](./examples).

## Ссылки

- Полная документация API: [developers.botix.pro](https://developers.botix.pro)
- Платформа BOTIX: [botix.pro](https://botix.pro)
- Для разработчиков: [botix.pro/developers](https://botix.pro/developers)
- Issues: [github.com/BOTIX-pro/sdk-python/issues](https://github.com/BOTIX-pro/sdk-python/issues)
- PyPI: [pypi.org/project/botix](https://pypi.org/project/botix)

## Лицензия

[MIT](./LICENSE) © 2026 BOTIX (ИП Шпагин В.В.)
