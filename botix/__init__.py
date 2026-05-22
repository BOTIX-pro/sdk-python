# coding: utf-8

"""
BOTIX SDK для Python — официальная клиентская библиотека публичного API BOTIX.

Точка входа — :class:`botix.Client`. Хелпер :func:`botix.verify_webhook`
сверяет подпись входящих webhook-сообщений.

Пример:

    import botix

    client = botix.Client("btx_live_...")
    print(client.me())
"""

__version__ = "1.0.0"

# Высокоуровневое API — то, что использует разработчик в 99% случаев.
from botix.client import Client as Client
from botix.idempotency import Response as Response
from botix.idempotency import generate_idempotency_key as generate_idempotency_key
from botix.webhook import verify_webhook as verify_webhook

# Низкоуровневые компоненты сгенерированного клиента — для опытных пользователей,
# которым нужен прямой доступ к сырому ApiClient / Configuration / типизированным
# pydantic-моделям ответов.
from botix.api.channels_api import ChannelsApi as ChannelsApi
from botix.api.chats_api import ChatsApi as ChatsApi
from botix.api.contacts_api import ContactsApi as ContactsApi
from botix.api.messages_api import MessagesApi as MessagesApi
from botix.api.scenarios_api import ScenariosApi as ScenariosApi
from botix.api.system_api import SystemApi as SystemApi
from botix.api.webhooks_api import WebhooksApi as WebhooksApi
from botix.api_client import ApiClient as ApiClient
from botix.api_response import ApiResponse as ApiResponse
from botix.configuration import Configuration as Configuration
from botix.exceptions import ApiAttributeError as ApiAttributeError
from botix.exceptions import ApiException as ApiException
from botix.exceptions import ApiKeyError as ApiKeyError
from botix.exceptions import ApiTypeError as ApiTypeError
from botix.exceptions import ApiValueError as ApiValueError
from botix.exceptions import OpenApiException as OpenApiException

# Типизированные модели данных — для type hints и сериализации.
from botix.models.channel import Channel as Channel
from botix.models.chat import Chat as Chat
from botix.models.contact import Contact as Contact
from botix.models.contact_writable import ContactWritable as ContactWritable
from botix.models.error import Error as Error
from botix.models.error_error import ErrorError as ErrorError
from botix.models.me_response import MeResponse as MeResponse
from botix.models.me_response_data import MeResponseData as MeResponseData
from botix.models.message import Message as Message
from botix.models.scenario import Scenario as Scenario
from botix.models.webhook import Webhook as Webhook
from botix.models.webhook_event import WebhookEvent as WebhookEvent

__all__ = [
    "__version__",
    # High-level
    "Client",
    "Response",
    "verify_webhook",
    "generate_idempotency_key",
    # Low-level (advanced) — resource API classes
    "ChannelsApi",
    "ChatsApi",
    "ContactsApi",
    "MessagesApi",
    "ScenariosApi",
    "SystemApi",
    "WebhooksApi",
    # Low-level — core
    "ApiClient",
    "ApiResponse",
    "Configuration",
    # Exceptions
    "ApiException",
    "ApiAttributeError",
    "ApiKeyError",
    "ApiTypeError",
    "ApiValueError",
    "OpenApiException",
    # Models
    "Channel",
    "Chat",
    "Contact",
    "ContactWritable",
    "Error",
    "ErrorError",
    "MeResponse",
    "MeResponseData",
    "Message",
    "Scenario",
    "Webhook",
    "WebhookEvent",
]
