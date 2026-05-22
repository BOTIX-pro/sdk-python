"""
Удобный высокоуровневый клиент BOTIX поверх автогенерированного ApiClient.

Пример:

    import botix

    client = botix.Client("btx_live_...")
    me = client.me()
    contacts = client.contacts.list(per_page=20)
    response = client.messages.send(contact_id=42, content="Привет!")
    if response.replayed:
        print("Это идемпотентный повтор — серверу запрос не пошёл")

Resources (доступны как свойства клиента):
    - ``client.contacts``  — CRM-карточка клиента
    - ``client.messages``  — история и отправка сообщений
    - ``client.scenarios`` — сценарии и их запуск
    - ``client.chats``     — диалоги
    - ``client.channels``  — подключённые каналы
    - ``client.webhooks``  — подписки на события
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from botix.api.default_api import DefaultApi
from botix.api.webhooks_api import WebhooksApi
from botix.api_client import ApiClient
from botix.configuration import Configuration
from botix.idempotency import Response, generate_idempotency_key
from botix.models.contact_writable import ContactWritable
from botix.models.public_v1_contacts_id_tags_post_request import (
    PublicV1ContactsIdTagsPostRequest,
)
from botix.models.public_v1_messages_post_request import PublicV1MessagesPostRequest
from botix.models.public_v1_messages_post_request_attachments_inner import (
    PublicV1MessagesPostRequestAttachmentsInner,
)
from botix.models.public_v1_scenarios_id_run_post_request import (
    PublicV1ScenariosIdRunPostRequest,
)
from botix.models.public_v1_webhooks_id_put_request import PublicV1WebhooksIdPutRequest
from botix.models.public_v1_webhooks_post_request import PublicV1WebhooksPostRequest
from botix.models.webhook_event import WebhookEvent

DEFAULT_HOST = "https://api.botix.pro"
DEFAULT_USER_AGENT = "botix-python/1.0.0"


class Client:
    """Главный класс BOTIX SDK.

    :param api_key: API-ключ (``btx_live_...``) — получается в кабинете
                    BOTIX в разделе «Настройки → API-ключи».
    :param host: базовый URL API. По умолчанию ``https://api.botix.pro``.
    :param timeout: общий тайм-аут одного HTTP-запроса в секундах. По умолчанию 30.
    :param auto_idempotency: автоматически генерировать ``Idempotency-Key`` для
                             мутирующих методов (``messages.send``, ``scenarios.run``)
                             если разработчик не передал явно. По умолчанию True.
    :param user_agent: значение заголовка ``User-Agent``.
                       По умолчанию ``botix-python/<version>``.
    """

    def __init__(
        self,
        api_key: str,
        host: str = DEFAULT_HOST,
        timeout: Optional[float] = 30.0,
        auto_idempotency: bool = True,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        if not api_key:
            raise ValueError("api_key обязателен (например, 'btx_live_...')")

        config = Configuration(host=host, access_token=api_key)
        api_client = ApiClient(configuration=config)
        api_client.user_agent = user_agent

        self._config = config
        self._api_client = api_client
        self._default_api = DefaultApi(api_client)
        self._webhooks_api = WebhooksApi(api_client)
        self._timeout = timeout
        self._auto_idempotency = auto_idempotency

        self.contacts = _Contacts(self)
        self.messages = _Messages(self)
        self.scenarios = _Scenarios(self)
        self.chats = _Chats(self)
        self.channels = _Channels(self)
        self.webhooks = _Webhooks(self)

    @property
    def api_client(self) -> ApiClient:
        """Низкоуровневый сгенерированный ApiClient — для опытных пользователей."""
        return self._api_client

    @property
    def auto_idempotency(self) -> bool:
        return self._auto_idempotency

    def close(self) -> None:
        """Закрыть HTTP-пул и освободить ресурсы. Сейчас no-op — urllib3
        пул-менеджер сгенерированного клиента живёт до GC. Метод оставлен
        ради совместимости с `with`-блоком."""
        return None

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def me(self) -> Any:
        """Контекст текущего ключа: project_id, scopes, plan_key, rate-limit."""
        return self._default_api.public_v1_me_get(
            _request_timeout=self._timeout,
        )


class _Resource:
    """База для resource-сабклиентов."""

    def __init__(self, client: Client) -> None:
        self._client = client
        self._api: DefaultApi = client._default_api
        self._timeout = client._timeout


class _Contacts(_Resource):
    def list(
        self,
        page: int = 1,
        per_page: int = 50,
        tag: Optional[str] = None,
        channel: Optional[str] = None,
        lead_status: Optional[str] = None,
        since: Optional[Any] = None,
    ) -> Any:
        return self._api.public_v1_contacts_get(
            page=page,
            per_page=per_page,
            tag=tag,
            channel=channel,
            lead_status=lead_status,
            since=since,
            _request_timeout=self._timeout,
        )

    def get(self, contact_id: int) -> Any:
        return self._api.public_v1_contacts_id_get(
            id=contact_id,
            _request_timeout=self._timeout,
        )

    def create(self, **fields: Any) -> Any:
        payload = ContactWritable.model_validate(fields)
        return self._api.public_v1_contacts_post(
            contact_writable=payload,
            _request_timeout=self._timeout,
        )

    def update(self, contact_id: int, **fields: Any) -> Any:
        payload = ContactWritable.model_validate(fields)
        return self._api.public_v1_contacts_id_put(
            id=contact_id,
            contact_writable=payload,
            _request_timeout=self._timeout,
        )

    def delete(self, contact_id: int) -> None:
        self._api.public_v1_contacts_id_delete(
            id=contact_id,
            _request_timeout=self._timeout,
        )

    def add_tag(self, contact_id: int, tag: str) -> Any:
        body = PublicV1ContactsIdTagsPostRequest(tag=tag)
        return self._api.public_v1_contacts_id_tags_post(
            id=contact_id,
            public_v1_contacts_id_tags_post_request=body,
            _request_timeout=self._timeout,
        )

    def remove_tag(self, contact_id: int, tag: str) -> Any:
        return self._api.public_v1_contacts_id_tags_tag_delete(
            id=contact_id,
            tag=tag,
            _request_timeout=self._timeout,
        )


class _Messages(_Resource):
    def list(
        self,
        page: int = 1,
        per_page: int = 50,
        contact_id: Optional[int] = None,
        chat_id: Optional[int] = None,
        channel: Optional[str] = None,
        role: Optional[str] = None,
        since: Optional[Any] = None,
    ) -> Any:
        return self._api.public_v1_messages_get(
            page=page,
            per_page=per_page,
            contact_id=contact_id,
            chat_id=chat_id,
            channel=channel,
            role=role,
            since=since,
            _request_timeout=self._timeout,
        )

    def send(
        self,
        contact_id: int,
        content: str,
        channel: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Response:
        """Отправить сообщение через канал. Возвращает обёртку Response.

        Проверьте ``response.replayed`` — True если BOTIX вернул
        ``Idempotent-Replayed: 1`` (повтор по совпадению Idempotency-Key).
        """
        atts: Optional[List[PublicV1MessagesPostRequestAttachmentsInner]] = None
        if attachments:
            atts = [
                PublicV1MessagesPostRequestAttachmentsInner.model_validate(a)
                for a in attachments
            ]
        body = PublicV1MessagesPostRequest(
            contact_id=contact_id,
            content=content,
            channel=channel,
            attachments=atts,
        )
        key = idempotency_key or (
            generate_idempotency_key() if self._client.auto_idempotency else None
        )
        api_response = self._api.public_v1_messages_post_with_http_info(
            public_v1_messages_post_request=body,
            idempotency_key=key,
            _request_timeout=self._timeout,
        )
        return Response.from_api_response(api_response)


class _Scenarios(_Resource):
    def list(self) -> Any:
        return self._api.public_v1_scenarios_get(_request_timeout=self._timeout)

    def run(
        self,
        scenario_id: int,
        contact_id: int,
        channel: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        force: bool = False,
        idempotency_key: Optional[str] = None,
    ) -> Response:
        """Запустить сценарий для контакта. Возвращает обёртку Response."""
        body = PublicV1ScenariosIdRunPostRequest(
            contact_id=contact_id,
            channel=channel,
            variables=variables,
            force=force,
        )
        key = idempotency_key or (
            generate_idempotency_key() if self._client.auto_idempotency else None
        )
        api_response = self._api.public_v1_scenarios_id_run_post_with_http_info(
            id=scenario_id,
            public_v1_scenarios_id_run_post_request=body,
            idempotency_key=key,
            _request_timeout=self._timeout,
        )
        return Response.from_api_response(api_response)


class _Chats(_Resource):
    def list(
        self,
        page: int = 1,
        per_page: int = 50,
        status: Optional[str] = None,
        channel: Optional[str] = None,
        contact_id: Optional[int] = None,
    ) -> Any:
        return self._api.public_v1_chats_get(
            page=page,
            per_page=per_page,
            status=status,
            channel=channel,
            contact_id=contact_id,
            _request_timeout=self._timeout,
        )

    def messages(self, chat_id: int, page: int = 1, per_page: int = 50) -> Any:
        return self._api.public_v1_chats_id_messages_get(
            id=chat_id,
            page=page,
            per_page=per_page,
            _request_timeout=self._timeout,
        )


class _Channels(_Resource):
    def list(self) -> Any:
        return self._api.public_v1_channels_get(_request_timeout=self._timeout)


class _Webhooks:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._api: WebhooksApi = client._webhooks_api
        self._timeout = client._timeout

    def list(self) -> Any:
        return self._api.public_v1_webhooks_get(_request_timeout=self._timeout)

    def create(self, url: str, events: List[Union[str, WebhookEvent]]) -> Any:
        evs = [WebhookEvent(e) if not isinstance(e, WebhookEvent) else e for e in events]
        body = PublicV1WebhooksPostRequest(url=url, events=evs)
        return self._api.public_v1_webhooks_post(
            public_v1_webhooks_post_request=body,
            _request_timeout=self._timeout,
        )

    def update(
        self,
        webhook_id: int,
        url: Optional[str] = None,
        events: Optional[List[Union[str, WebhookEvent]]] = None,
        status: Optional[str] = None,
    ) -> Any:
        evs: Optional[List[WebhookEvent]] = None
        if events is not None:
            evs = [WebhookEvent(e) if not isinstance(e, WebhookEvent) else e for e in events]
        body = PublicV1WebhooksIdPutRequest(url=url, events=evs, status=status)
        return self._api.public_v1_webhooks_id_put(
            id=webhook_id,
            public_v1_webhooks_id_put_request=body,
            _request_timeout=self._timeout,
        )

    def delete(self, webhook_id: int) -> None:
        self._api.public_v1_webhooks_id_delete(
            id=webhook_id,
            _request_timeout=self._timeout,
        )

    def test(self, webhook_id: int) -> Any:
        return self._api.public_v1_webhooks_id_test_post(
            id=webhook_id,
            _request_timeout=self._timeout,
        )
