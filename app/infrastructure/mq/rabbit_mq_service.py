import asyncio
import ssl
import logging
import os
from urllib.parse import quote

from dotenv import load_dotenv
from typing import Optional, AsyncGenerator, Callable
from aio_pika import connect_robust, Message, Connection, Channel
from tenacity import retry, stop_after_attempt, wait_exponential


from app.application.services.generation.dto.mq import MQPublishMessage
from app.core.decorators import log_errors

load_dotenv()

class RabbitMQService:
    def __init__(
            self,
            hostname = os.getenv('RABBITMQ_HOST'),
            vhost = os.getenv('RABBITMQ_VHOST'),
            username = os.getenv('RABBITMQ_USERNAME'),
            password = os.getenv('RABBITMQ_PASSWORD'),
            publish_queue = os.getenv('RABBITMQ_PUBLISH_QUEUE'),
            consume_queue = os.getenv('RABBITMQ_CONSUME_QUEUE')
    ):
        self.publish_queue = publish_queue
        self.consume_queue = consume_queue
        self.connection: Optional[Connection] = None
        self.channel: Optional[Channel] = None

        encoded_password = quote(password, safe='')
        encoded_vhost = quote(vhost, safe='') if vhost else ''

        url = f"amqp://{username}:{encoded_password}@{hostname}:5671/{encoded_vhost}"
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

        self.connect_kwargs = {
            "url": url,
            "ssl_context": ssl_context,
            "heartbeat": 360,
            "timeout": 300
        }

    @log_errors("Failed to connect to RabbitMQ")
    async def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await connect_robust(**self.connect_kwargs)
        if not self.channel or self.channel.is_closed:
            self.channel = await self.connection.channel()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _reconnect(self):
        logging.warning("RabbitMQ connection is closed. Trying Reconnection...")
        await self.connect()

    @log_errors("RabbitMQ publish failed")
    async def publish(self, message: MQPublishMessage):
        if self.connection.is_closed or self.channel.is_closed:
            await self._reconnect()

        await self.channel.default_exchange.publish(
            Message(
                body=message.to_json(),
                delivery_mode=2
            ),
            routing_key=self.publish_queue
        )

    @log_errors("RabbitMQ consume failed")
    async def consume(self, sync_callback: Callable):
        if self.connection.is_closed or self.channel.is_closed:
            await self._reconnect()

        async def async_wrapper(message):
            async with message.process():
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, sync_callback, message.body)

        queue = await self.channel.declare_queue(self.consume_queue, passive=True)

        await queue.consume(async_wrapper)

    async def get_queue_info(self):
        if self.connection.is_closed or self.channel.is_closed:
            await self._reconnect()

        queue = await self.channel.declare_queue(self.publish_queue, passive=True)
        message_count = queue.declaration_result.message_count
        consumer_count = queue.declaration_result.consumer_count
        return message_count, consumer_count

    async def close(self):
        if self.channel and not self.channel.is_closed:
            await self.channel.close()
        if self.connection and not self.connection.is_closed:
            await self.connection.close()


async def get_rabbit_mq_service() -> AsyncGenerator[RabbitMQService, None]:
    rabbit_mq_service = RabbitMQService()
    await rabbit_mq_service.connect()
    try:
        yield rabbit_mq_service
    finally:
        await rabbit_mq_service.close()