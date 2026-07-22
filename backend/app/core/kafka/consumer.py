import json
from confluent_kafka import Consumer, KafkaError, KafkaException
from app.core.logger import logger
from app.core.config import settings
from .config import kafka_config

class KafkaConsumer:
    def __init__(self):
        conf = kafka_config.copy()
        conf["client.id"] = "speech_analytics_consumer"
        self.consumer = Consumer(conf)
        self.topic = settings.KAFKA_TOPIC_ANALYSIS
        self.consumer.subscribe([self.topic])
        self._is_closed = False
        logger.info(f"Consumer connected to {settings.KAFKA_BOOTSTRAP_SERVERS}")

    def check_health(self):
        try:
            self.consumer.list_topics(timeout=3.0)
            return True
        except KafkaException as e:
            logger.error(f"Broker unavailable: {e}")
            return False

    def consume(self, process_func, timeout=1.0):
        if self._is_closed:
            return
        try:
            msg = self.consumer.poll(timeout)
            if msg is None:
                return
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug(f"End of partition reached {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                else:
                    raise KafkaException(msg.error())
            else:
                value = msg.value().decode('utf-8')
                data = json.loads(value)
                process_func(data)
                self.consumer.commit(message=msg, asynchronous=False)
                logger.debug(f"Message committed for {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
        except Exception as e:
            logger.error(f"Error while consuming message: {e}")

    def close(self):
        if not self._is_closed:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            self._is_closed = True
