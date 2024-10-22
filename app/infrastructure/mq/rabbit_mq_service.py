import os

import pika
import ssl

from fastapi.params import Depends
from pydantic import BaseModel

from app.application.services.generation.manage_generation import ManageGenerationApplicationService, \
    get_manage_generation_application_service


class RabbitMQService:
    def __init__(
            self,
            url,
            username,
            password,
            vhost,
            consume_queue,
            publish_queue,
            on_message_callback
    ):
        self.channel = self._create_channel(url, username, password, vhost)
        self.consume_queue = consume_queue
        self.publish_queue = publish_queue
        self.on_message_callback = on_message_callback

    def _create_channel(self, url: str, username: str, password: str, vhost: str):
        cred = pika.PlainCredentials(username=username, password=password)
        cxt = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_options = pika.SSLOptions(context=cxt, server_hostname=url)

        conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=url, credentials=cred, virtual_host=vhost, ssl_options=ssl_options, heartbeat=360)
        )
        return conn.channel()

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            self.consume_queue,
            on_message_callback=self.on_message_callback,
            auto_ack=False
        )
        self.channel.start_consuming()

    def publish(self, message: BaseModel):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.publish_queue,
            body=message.model_dump_json().encode('utf-8')
        )

    def get_queue_info(self):
        queue_info = self.channel.queue_declare(queue=self.publish_queue, passive=True)

        message_count = queue_info.method.message_count
        consumer_count = queue_info.method.consumer_count
        return message_count, consumer_count

def get_on_message_callback_func(
        instance: ManageGenerationApplicationService = Depends(get_manage_generation_application_service)
):
    return instance.on_mq_message

def get_rabbit_mq_service(
        on_message_callback = Depends(get_on_message_callback_func)
) -> RabbitMQService:
    mq_service = RabbitMQService(
        url=os.getenv("RABBIT_MQ_URL"),
        username=os.getenv("RABBIT_MQ_USERNAME"),
        password=os.getenv("RABBIT_MQ_PASSWORD"),
        vhost=os.getenv("RABBIT_MQ_VHOST"),
        consume_queue=os.getenv("RABBIT_MQ_CONSUME_QUEUE"),
        publish_queue=os.getenv("RABBIT_MQ_PUBLISH_QUEUE"),
        on_message_callback=on_message_callback
    )
    mq_service.start_consuming()
    return mq_service