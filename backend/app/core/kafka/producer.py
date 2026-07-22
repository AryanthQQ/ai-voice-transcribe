import json
from confluent_kafka import Producer, KafkaException
from app.core.logger import logger
from app.core.config import settings

class KafkaProducer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KafkaProducer, cls).__new__(cls)
            conf = {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "client.id": "speech_analytics_producer",
                "acks": "all",
                "retries": 3,
                "enable.idempotence": True,
                "compression.type": "lz4",
                "linger.ms": 5,
                "batch.num.messages": 100,
            }
            cls._instance.producer = Producer(conf)
            cls._instance.topic = settings.KAFKA_TOPIC_ANALYSIS
            cls._instance._is_closed = False
            logger.info(f"Producer connected to {settings.KAFKA_BOOTSTRAP_SERVERS}")
        return cls._instance

    def check_health(self):
        try:
            self.producer.list_topics(timeout=3.0)
            return True
        except KafkaException as e:
            logger.error(f"Broker unavailable: {e}")
            return False

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message published to {msg.topic()} [{msg.partition()}]")

    def produce(self, message: dict):
        if self._is_closed:
            return
        try:
            value = json.dumps(message).encode('utf-8')
            self.producer.produce(
                topic=self.topic,
                value=value,
                callback=self.delivery_report
            )
            self.producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")

    def close(self):
        if not self._is_closed:
            logger.info("Flushing Kafka producer...")
            self.producer.flush()
            self._is_closed = True
