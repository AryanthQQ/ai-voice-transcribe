from app.core.config import settings

kafka_config = {
    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
    "group.id": settings.KAFKA_CONSUMER_GROUP,
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
}
