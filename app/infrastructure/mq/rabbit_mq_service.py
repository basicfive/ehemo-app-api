import asyncio
import ssl
import logging
from urllib.parse import quote

from typing import Optional, AsyncGenerator, Callable
from aio_pika import connect_robust, Message, Connection, Channel
from tenacity import retry, stop_after_attempt, wait_exponential

from app.application.services.generation.dto.mq import MQPublishMessage
from app.core.decorators import log_errors
from app.core.config import rabbit_mq_setting
from app.core.enums.message_priority import MessagePriority

logger = logging.getLogger()

class RabbitMQService:
    def __init__(
            self,
            hostname: str = rabbit_mq_setting.RABBITMQ_HOST,
            vhost: str = rabbit_mq_setting.RABBITMQ_VHOST,
            username: str = rabbit_mq_setting.RABBITMQ_USERNAME,
            password: str = rabbit_mq_setting.RABBITMQ_PASSWORD,
            publish_queue: str = rabbit_mq_setting.RABBITMQ_PUBLISH_QUEUE,
            consume_queue: str = rabbit_mq_setting.RABBITMQ_CONSUME_QUEUE
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
            "heartbeat": 300,
            "timeout": 300
        }

    @log_errors("Failed to connect to RabbitMQ")
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
        await self.connect()

    @log_errors("RabbitMQ publish failed")
    async def publish(self, message: MQPublishMessage, expiration_sec: int, priority: int = MessagePriority.LOW):
        if self.connection.is_closed or self.channel.is_closed:
            await self._reconnect()

        await self.channel.default_exchange.publish(
            Message(
                body=message.to_json(),
                delivery_mode=2,
                expiration=expiration_sec,
                priority=priority
            ),
            routing_key=self.publish_queue
        )
        logger.info(f"[MQ] Published Job ID: {message.image_generation_job_id}. DETAILS: {message.to_str()}")

    async def consume(self, sync_callback: Callable):
        while True:  # 지속적인 재시도를 위한 루프
            try:
                if self.connection.is_closed or self.channel.is_closed:
                    await self._reconnect()

                queue = await self.channel.declare_queue(self.consume_queue, passive=True)

                async def async_wrapper(message):
                    try:
                        async with message.process(requeue=True):  # requeue 옵션 추가
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, sync_callback, message.body)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}", exc_info=True)
                        # connection 문제면 재연결 시도
                        if isinstance(e, (ConnectionError, TimeoutError)):
                            await self._reconnect()
                        raise  # 다시 throw해서 메시지가 requeue되도록 함

                await queue.consume(async_wrapper)

                # consume이 시작된 후 connection 상태 모니터링
                while not (self.connection.is_closed or self.channel.is_closed):
                    await asyncio.sleep(30)  # 30초마다 체크

                logger.warning("Connection or channel closed, restarting consumer...")

            except Exception as e:
                logger.error(f"Consumer encountered an error: {e}", exc_info=True)
                await asyncio.sleep(5)  # 에러 발생 시 잠시 대기 후 재시도

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