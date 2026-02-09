import json
from aiokafka import AIOKafkaProducer
from app.settings import settings

_producer: AIOKafkaProducer | None = None

async def start_kafka():
    global _producer
    _producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        client_id=settings.KAFKA_CLIENT_ID,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await _producer.start()

async def stop_kafka():
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None

async def emit(topic: str, event: dict):
    if not _producer:
        return
    await _producer.send_and_wait(topic, event)
