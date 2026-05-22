# Changelog

Все значимые изменения проекта документируются здесь. Формат — [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/), версии следуют [Semantic Versioning](https://semver.org/lang/ru/).

## [1.1.0] - 2026-05-22

### Added

- 3 новых bulk endpoint: `contacts.bulk_create`, `contacts.bulk_update`, `messages.bulk_send` (до 100 операций за запрос, частичный успех, идемпотентность 24ч).
- Параметр `cursor` в list-методах (`contacts.list`, `messages.list`, `chats.list`, `chats.messages`) — cursor-based пагинация параллельно с существующим `page`/`per_page`.
- Параметр `limit` в cursor-режиме list-методов (размер страницы 1..100).
- Поле `meta.next_cursor` в response list-методов (opaque cursor для следующей страницы; `null` = последняя).
- Описание заголовков `X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset` (во всех ответах) и `Retry-After` (в 429).
- 12 новых pydantic-моделей: `BulkResult`, `ContactsBulkCreateRequest`, `MessagesBulkSendRequest` и другие — экспортируются из `botix`.

### Changed

- Регенерация SDK на основе `openapi.yaml` v1.1.0 (`openapi-generator-cli`, generator `python`, `packageVersion=1.1.0`).

### Compatibility

- Изменения обратно-совместимые. Все вызовы v1.0 продолжают работать без правок.

## [1.0.0] - 2026-05-22

### Added

- Первый публичный релиз официального Python SDK для BOTIX.
- Поддержка всех 21 эндпоинта Public API V1 BOTIX (контакты, сообщения, сценарии, чаты, каналы, webhooks).
- Класс `botix.Client` — высокоуровневая инициализация в одну строку с автоматическим Bearer-токеном.
- Resource-сабклиенты: `client.contacts`, `client.messages`, `client.scenarios`, `client.chats`, `client.channels`, `client.webhooks`.
- Хелпер `botix.verify_webhook(raw_payload, signature_header, secret)` — проверка HMAC-SHA256 подписи входящих webhook через `hmac.compare_digest` (timing-safe).
- Авто-генерация заголовка `Idempotency-Key` (UUID v4) на мутирующих методах `messages.send` и `scenarios.run`; отключается опцией `auto_idempotency=False`.
- Обёртка `botix.Response` с флагом `replayed` — True, если сервер вернул `Idempotent-Replayed: 1`.
- Типизированные pydantic-модели для всех схем OpenAPI.
- Примеры использования в `examples/`.
- CI GitHub Actions с матрицей Python 3.9 / 3.10 / 3.11 / 3.12.
