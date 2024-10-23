# import os
# import threading
# import pika
# import ssl
# from pydantic import BaseModel
# from typing import Optional
# from dotenv import load_dotenv
#
#
# class RabbitMQService:
#     _instance: Optional['RabbitMQService'] = None
#     _lock = threading.Lock()
#     _is_initialized = False
#
#     def __new__(cls) -> 'RabbitMQService':
#         if cls._instance is None:
#             with cls._lock:
#                 if cls._instance is None:
#                     cls._instance = super().__new__(cls)
#         return cls._instance
#
#     def initialize(
#             self,
#             url,
#             username,
#             password,
#             vhost,
#             port,
#             consume_queue,
#             publish_queue,
#             on_message_callback
#     ) -> None:
#         """Thread-safe initialization"""
#         with self._lock:
#             if not self._is_initialized:
#                 self.channel = self.__create_channel(url, username, password, vhost, port)
#                 self.publish_queue = publish_queue
#                 self.__start_consuming_in_thread(consume_queue, on_message_callback)
#                 self._is_initialized = True
#
#     def __create_channel(self, url: str, username: str, password: str, vhost: str, port: int):
#         cred = pika.PlainCredentials(username=username, password=password)
#         cxt = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
#         ssl_options = pika.SSLOptions(context=cxt, server_hostname=url)
#         conn = pika.BlockingConnection(
#             pika.ConnectionParameters(
#                 host=url,
#                 credentials=cred,
#                 port=port,
#                 virtual_host=vhost,
#                 ssl_options=ssl_options,
#                 heartbeat=360
#             )
#         )
#         return conn.channel()
#
#     def __start_consuming_in_thread(self, consume_queue, on_message_callback):
#         def consume():
#             self.channel.basic_consume(
#                 queue=consume_queue,
#                 on_message_callback=on_message_callback,
#                 auto_ack=False
#             )
#             self.channel.start_consuming()
#
#         thread = threading.Thread(target=consume, daemon=True)
#         thread.start()
#
#     def publish(self, message: BaseModel):
#         self.channel.basic_publish(
#             exchange='',
#             routing_key=self.publish_queue,
#             body=message.model_dump_json().encode('utf-8')
#         )
#
#     def get_queue_info(self):
#         queue_info = self.channel.queue_declare(queue=self.publish_queue, passive=True)
#         message_count = queue_info.method.message_count
#         consumer_count = queue_info.method.consumer_count
#         return message_count, consumer_count
#
#
# # 싱글톤 인스턴스를 얻기 위한 함수
# def get_rabbit_mq_service() -> RabbitMQService:
#     return RabbitMQService()
#
#
# # FastAPI 시작 시 RabbitMQ 서비스 초기화 예시
# def initialize_rabbit_mq(on_message_callback):
#     load_dotenv()
#     rabbit_mq = get_rabbit_mq_service()
#     rabbit_mq.initialize(
#         url=os.getenv("RABBIT_MQ_URL"),
#         username=os.getenv("RABBIT_MQ_USERNAME"),
#         password=os.getenv("RABBIT_MQ_PASSWORD"),
#         vhost=os.getenv("RABBIT_MQ_VHOST"),
#         port=os.getenv("RABBIT_MQ_PORT"),
#         consume_queue=os.getenv("RABBIT_MQ_CONSUME_QUEUE"),
#         publish_queue=os.getenv("RABBIT_MQ_PUBLISH_QUEUE"),
#         on_message_callback=on_message_callback
#     )

from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exceptions import StreamLostError, AMQPConnectionError
import ssl
import threading
from typing import Optional
import logging
import pika
import os
import time
from dotenv import load_dotenv

from app.application.services.generation.dto.mq import MQPublishMessage

load_dotenv()

class RabbitMQService:
    def __init__(self):
        self.connection: Optional[BlockingConnection] = None
        self.channel = None
        self.publish_queue = os.getenv('RABBITMQ_PUBLISH_QUEUE')
        self.consume_queue = os.getenv('RABBITMQ_CONSUME_QUEUE')
        self._lock = threading.Lock()
        self._connect_lock = threading.Lock()

    def _create_ssl_context(self):
        # SSL 컨텍스트 생성
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context

    def _get_connection_params(self):
        # 연결 파라미터 설정
        return ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST'),
            port=5671,  # SSL 포트
            virtual_host=os.getenv('RABBITMQ_VHOST'),
            credentials=PlainCredentials(
                os.getenv('RABBITMQ_USERNAME'),
                os.getenv('RABBITMQ_PASSWORD')
            ),
            ssl_options=pika.SSLOptions(context=self._create_ssl_context()),
            connection_attempts=3,
            retry_delay=5,
            heartbeat=60,  # heartbeat 추가
            blocked_connection_timeout=300
        )

    def ensure_connection(self):
        """스레드 세이프한 연결 보장"""
        with self._connect_lock:
            try:
                if not self.connection or not self.connection.is_open:
                    self.connection = BlockingConnection(self._get_connection_params())
                    self.channel = self.connection.channel()
            except (StreamLostError, AMQPConnectionError) as e:
                logging.error(f"RabbitMQ connection error: {e}")
                # 연결 실패시 기존 연결 정리
                self.cleanup()
                raise

    def cleanup(self):
        """연결 정리"""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
        finally:
            self.channel = None
            self.connection = None

    def publish(self, message: MQPublishMessage):
        """메시지 발행 with 재시도 로직"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self._lock:
                    self.ensure_connection()
                    self.channel.basic_publish(
                        exchange='',
                        routing_key=self.publish_queue,
                        body=message.to_json(),
                        properties=pika.BasicProperties(
                            delivery_mode=2  # persistent message
                        )
                    )
                return
            except (StreamLostError, AMQPConnectionError) as e:
                logging.error(f"Publish attempt {attempt + 1} failed: {e}")
                self.cleanup()
                if attempt == max_retries - 1:
                    raise
                continue

    def consume(self, callback):
        """컨슈머 설정"""

        def wrapped_callback(ch, method, properties, body):
            try:
                callback(ch, method, properties, body)
            except Exception as e:
                logging.error(f"Error in consumer callback: {e}")
                # 에러 발생시 메시지 reject
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)

        while True:
            try:
                self.ensure_connection()
                self.channel.basic_consume(
                    queue=self.consume_queue,
                    on_message_callback=wrapped_callback
                )
                self.channel.start_consuming()
            except (StreamLostError, AMQPConnectionError) as e:
                logging.error(f"Consumer connection lost: {e}")
                self.cleanup()
                time.sleep(5)  # 재연결 전 딜레이
                continue
            except Exception as e:
                logging.error(f"Unexpected error in consumer: {e}")
                self.cleanup()
                raise

    def get_queue_info(self):
        queue_info = self.channel.queue_declare(queue=self.publish_queue, passive=True)
        message_count = queue_info.method.message_count
        consumer_count = queue_info.method.consumer_count
        return message_count, consumer_count

    def __del__(self):
        self.cleanup()

# 싱글톤 인스턴스를 얻기 위한 함수
def get_rabbit_mq_service() -> RabbitMQService:
    return RabbitMQService()
