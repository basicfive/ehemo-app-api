import asyncio
from typing import Dict
import ssl
import logging
from urllib.parse import quote

from typing import Optional, AsyncGenerator, Callable
from aio_pika import connect_robust, Message, Connection, Channel
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import rabbit_mq_settings, base_settings
from app.core.enums.message_priority import MessagePriority
from app.infrastructure.alert.discord_webhook import send_error_notification

logger = logging.getLogger()

class RabbitMQService:
    _instances: Dict[str, 'RabbitMQService'] = {}
    _lock = asyncio.Lock()

    def __init__(
            self,
            connection_name: str,
            hostname: str = rabbit_mq_settings.RABBITMQ_HOST,
            vhost: str = rabbit_mq_settings.RABBITMQ_VHOST,
            port: int = rabbit_mq_settings.RABBITMQ_PORT,
            username: str = rabbit_mq_settings.RABBITMQ_USERNAME,
            password: str = rabbit_mq_settings.RABBITMQ_PASSWORD,
    ):
        self.connection_name = connection_name
        self.connection: Optional[Connection] = None
        self.channel: Optional[Channel] = None

        encoded_password = quote(password, safe='')
        encoded_vhost = quote(vhost, safe='') if vhost else ''

        url = f"amqp://{username}:{encoded_password}@{hostname}:{port}/{encoded_vhost}"
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

        self.connect_kwargs = {
            "url": url,
            "ssl_context": ssl_context,
            "heartbeat": 300,
            "timeout": 300,
            "client_properties": {
                "connection_name": connection_name
            }
        }

    @classmethod
    async def get_instance(cls, connection_name: str) -> 'RabbitMQService':
        async with cls._lock:
            if connection_name not in cls._instances:
                instance = cls(connection_name=connection_name)
                await instance.connect()
                cls._instances[connection_name] = instance
            return cls._instances[connection_name]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await connect_robust(**self.connect_kwargs)
        if not self.channel or self.channel.is_closed:
            self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _reconnect(self):
        logging.warning("RabbitMQ connection is closed. Trying Reconnection...")
        await self.close()  # 기존 연결 정리 후
        await self.connect()

    async def publish(
            self,
            message: str,
            queue_name: str,
            expiration_sec: Optional[int] = None,
            priority: int = MessagePriority.LOW
        ):
        if self.connection.is_closed or self.channel.is_closed:
            await self._reconnect()

        message_params = {
            "body": message.encode('utf-8'),
            "delivery_mode": 2,  # persistent message
            "priority": priority
        }
        if expiration_sec:
            message_params["expiration"] = expiration_sec

        await self.channel.default_exchange.publish(
            Message(**message_params),
            routing_key=queue_name
        )
        logger.info(f"[MQ] Published message to {queue_name}. message: {message}")


    async def consume(
            self,
            queue_name: str,
            callback: Callable,
    ):
        while True:
            try:
                if self.connection.is_closed or self.channel.is_closed:
                    await self._reconnect()

                queue = await self.channel.get_queue(queue_name)

                async def message_handler(message):
                    try:
                        await callback(message.body)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}", exc_info=True)
                        send_error_notification(webhook_url=base_settings.ALERT_DISCORD_WEBHOOK, error=e)

                # no_ack=True로 설정, context manager 사용하지 않음
                await queue.consume(message_handler, no_ack=True)

                while not (self.connection.is_closed or self.channel.is_closed):
                    await asyncio.sleep(30)

                # 연결이 끊어졌음을 로그로 남기고 while True로 인해 처음부터 다시 시작
                logger.warning("Connection or channel closed, will attempt to reconnect...")

            except Exception as e:
                logger.error(f"Consumer encountered an error: {e}", exc_info=True)
                send_error_notification(webhook_url=base_settings.ALERT_DISCORD_WEBHOOK, error=e)
                await asyncio.sleep(5)


    async def get_queue_info(self, queue_name: str):
        if self.connection.is_closed or self.channel.is_closed:
            await self._reconnect()

        queue = await self.channel.declare_queue(queue_name, passive=True)
        message_count = queue.declaration_result.message_count
        consumer_count = queue.declaration_result.consumer_count
        return message_count, consumer_count

    async def close(self):
        if self.channel and not self.channel.is_closed:
            await self.channel.close()
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
        async with self._lock:
            if self.connection_name in self._instances:
                del self._instances[self.connection_name]

async def get_rabbit_mq_service() -> AsyncGenerator[RabbitMQService, None]:
    service = await RabbitMQService.get_instance("rabbit_mq_service")
    try:
        yield service
    finally:
        pass

async def get_rabbit_mq_service_singleton() -> RabbitMQService:
    return await RabbitMQService.get_instance("rabbit_mq_service")