"""Defines core consumer functionality"""
import logging

import confluent_kafka
from confluent_kafka import Consumer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from tornado import gen


logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Defines the base kafka consumer class"""

    def __init__(
        self,
        topic_name_pattern,
        message_handler,
        is_avro=True,
        offset_earliest=False,
        sleep_secs=1.0,
        consume_timeout=0.1,
    ):
        """Creates a consumer object for asynchronous use"""
        self.topic_name_pattern = topic_name_pattern
        self.message_handler = message_handler
        self.sleep_secs = sleep_secs
        self.consume_timeout = consume_timeout
        self.offset_earliest = offset_earliest

        self.broker_properties = {
            'bootstrap.servers': 'localhost:9092',
            "auto.offset.reset": "earliest" if offset_earliest else "latest",
            'group.id': '1'
        }

        if is_avro is True:
            self.broker_properties["schema.registry.url"] = "http://localhost:8081"
            self.consumer = AvroConsumer(self.broker_properties)
        else:
            self.consumer = Consumer(self.broker_properties)
        self.consumer.subscribe([self.topic_name_pattern], on_assign=self.on_assign)
        
    def on_assign(self, consumer, partitions):
        """Callback for when topic assignment takes place"""
        logger.info("on_assign is incomplete - skipping")
        for partition in partitions:
            if self.offset_earliest:
                partition.offset = "earliest"
        logger.info("partitions assigned for %s", self.topic_name_pattern)
        consumer.assign(partitions)

    async def consume(self):
        """Asynchronously consumes data from kafka topic"""
        while True:
            num_results = 1
            while num_results > 0:
                num_results = self._consume()
            await gen.sleep(self.sleep_secs)

    def _consume(self):
        """Polls for a message. Returns 1 if a message was received, 0 otherwise"""
        msg = self.consumer.poll(1)
        if msg is None:
            return 0
        try:
            if msg.error():
                logger.error(f"Error: {msg.error()}")
            else:
                self.message_handler(msg)
        except Exception as e:
            logger.error(e)
            
        return 1


    def close(self):
        """Cleans up any open kafka consumers"""
        self.consumer.close()