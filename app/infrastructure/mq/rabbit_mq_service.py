import asyncio
from typing import Dict
import ssl
import logging
from urllib.parse import quote

from typing import Optional, AsyncGenerator, Callable
from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractConnection, AbstractChannel

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
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self._connection_lock = asyncio.Lock()  # 연결 시도 동시 방지용 락

        encoded_password = quote(password, safe='')
        encoded_vhost = quote(vhost, safe='') if vhost else ''

        self.url = f"amqp://{username}:{encoded_password}@{hostname}:{port}/{encoded_vhost}"
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

        self.connect_kwargs = {
            "url": self.url,
            "ssl_context": self.ssl_context,
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
                await instance.ensure_connected()
                cls._instances[connection_name] = instance
            return cls._instances[connection_name]
    
    def _is_connection_valid(self) -> bool:
        """연결과 채널이 유효한지 확인합니다."""
        return (self.connection is not None and 
                not self.connection.is_closed and 
                self.channel is not None and 
                not self.channel.is_closed)
    
    async def connect(self):
        """
        새로운 MQ 연결을 설정합니다. 기존 연결이 있더라도 항상 새 연결을 생성합니다.
        처음 5번은 5초마다 재시도, 그 이후에는 1분마다 연결이 성공할 때까지 계속 재시도합니다.
        """
        # 기존 연결 정리
        await self._close_connection()
        
        retry_count = 0
        initial_retries = 5
        initial_retry_delay = 5
        extended_retry_delay = 60
        
        logger.info(f"RabbitMQ 연결 시도 중... Connection name: {self.connection_name}")
        
        while True:
            try:
                # 연결 시도
                self.connection = await connect_robust(**self.connect_kwargs)
                self.channel = await self.connection.channel()
                await self.channel.set_qos(prefetch_count=10)
                
                logger.info("RabbitMQ 연결 성공!")
                return
                
            except Exception as e:
                retry_count += 1
                
                if retry_count <= initial_retries:
                    delay = initial_retry_delay
                    logger.warning(f"RabbitMQ 연결 실패, {delay}초 후 재시도 ({retry_count}/{initial_retries})... 오류: {str(e)}")
                else:
                    delay = extended_retry_delay
                    logger.warning(f"RabbitMQ 연결 실패, {delay}초 후 재시도 중... (시도 횟수: {retry_count}) 오류: {str(e)}")
                
                # 다음 시도 전 대기
                await asyncio.sleep(delay)
                
                # 기존 연결 정리 (실패했을 수도 있으므로)
                await self._close_connection()
    
    async def ensure_connected(self):
        """
        연결 상태를 확인하고, 필요한 경우 연결을 수행합니다.
        이미 유효한 연결이 있으면 아무것도 하지 않습니다.
        """
        async with self._connection_lock:
            if not self._is_connection_valid():
                await self.connect()

    async def _close_connection_due_to_error(self, error: Exception):
        """연결 종료 중 오류가 발생한 경우 오류를 전송하고 연결을 종료합니다."""
        send_error_notification(webhook_url=base_settings.ALERT_DISCORD_WEBHOOK, error=error)
        await self._close_connection()

    async def _close_connection(self):
        """내부적으로 연결과 채널을 안전하게 닫습니다."""
        if self.channel and not self.channel.is_closed:
            try:
                await self.channel.close()
            except Exception as e:
                logger.debug(f"채널 종료 중 오류 (무시됨): {e}")
            finally:
                self.channel = None
            
        if self.connection and not self.connection.is_closed:
            try:
                await self.connection.close()
            except Exception as e:
                logger.debug(f"연결 종료 중 오류 (무시됨): {e}")
            finally:
                self.connection = None

    async def publish(
            self,
            message: str,
            queue_name: str,
            expiration_sec: Optional[int] = None,
            priority: int = MessagePriority.LOW
        ):
        """
        메시지를 발행하고, 연결 문제 발생 시 재연결을 시도합니다.
        publish 작업은 연결이 성공할 때까지 재시도합니다.
        """
        while True:
            try:
                # 연결 확인 및 필요시 재연결
                await self.ensure_connected()
                
                # 메시지 발행 준비
                message_params = {
                    "body": message.encode('utf-8'),
                    "delivery_mode": 2,  # persistent message
                    "priority": priority
                }
                if expiration_sec:
                    message_params["expiration"] = expiration_sec

                # 메시지 발행
                await self.channel.default_exchange.publish(
                    Message(**message_params),
                    routing_key=queue_name
                )
                logger.info(f"[MQ] Published message to {queue_name}. message: {message}")
                return  # 성공하면 반환
                
            except Exception as e:
                logger.error(f"메시지 발행 중 오류: {e}, 재연결 시도 중...")
                # 연결 무효화하여 다음 반복에서 재연결 시도
                await self._close_connection_due_to_error(e)
                await asyncio.sleep(1)  # 잠시 대기 후 재시도

    async def consume(
            self,
            queue_name: str,
            callback: Callable,
    ):
        """
        메시지 소비를 시작하고, 연결 문제 발생 시 재연결을 시도합니다.
        연결이 끊어지면 재연결 후 소비를 다시 시작합니다.
        """
        while True:
            try:
                # 연결 확인 및 필요시 재연결
                await self.ensure_connected()
                
                # 큐 가져오기
                queue = await self.channel.get_queue(queue_name)

                # 메시지 핸들러 정의
                async def message_handler(message):
                    try:
                        await callback(message.body)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}", exc_info=True)
                        send_error_notification(webhook_url=base_settings.ALERT_DISCORD_WEBHOOK, error=e)

                # 소비 시작 - consume은 비동기로 백그라운드에서 작동함
                consumer_tag = await queue.consume(message_handler, no_ack=True)
                logger.info(f"[MQ] Started consuming messages from {queue_name}, consumer_tag: {consumer_tag}")
                
                # 연결이 살아있는 동안 대기 (30초마다 확인)
                # RobustConnection에는 wait_closed 메소드가 없으므로, 주기적으로 상태 확인
                while self._is_connection_valid():
                    await asyncio.sleep(30)

                error_msg = f"RabbitMQ 연결이 닫힘. {queue_name} 소비자 재시작 준비 중..."
                logger.warning(error_msg)
                # 연결 정리
                await self._close_connection_due_to_error(error=Exception(error_msg))
                
            except Exception as e:
                logger.error(f"소비 중 오류: {e}, 재연결 시도 중...", exc_info=True)
                # 연결 무효화하여 다음 반복에서 재연결 시도
                await self._close_connection_due_to_error(e)
                await asyncio.sleep(5)  # 잠시 대기 후 다시 시작

    async def get_queue_info(self, queue_name: str):
        """큐 정보를 조회하고, 연결 문제 발생 시 재연결을 시도합니다."""
        while True:
            try:
                # 연결 확인 및 필요시 재연결
                await self.ensure_connected()
                
                # 큐 정보 조회
                queue = await self.channel.declare_queue(queue_name, passive=True)
                message_count = queue.declaration_result.message_count
                consumer_count = queue.declaration_result.consumer_count
                return message_count, consumer_count
                
            except Exception as e:
                logger.error(f"큐 정보 조회 중 오류: {e}, 재연결 시도 중...")
                # 연결 무효화하여 다음 반복에서 재연결 시도
                await self._close_connection_due_to_error(e)
                await asyncio.sleep(1)  # 잠시 대기 후 재시도

    async def close(self):
        """서비스 종료 시 연결과 채널을 닫고 인스턴스를 제거합니다."""
        await self._close_connection()
        
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