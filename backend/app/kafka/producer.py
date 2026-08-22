import json
import logging
import os

from confluent_kafka import Producer

from app.kafka.events import EVENTS_TOPIC

logger = logging.getLogger(__name__)

_producer = None


def get_producer():
    global _producer

    if _producer is None:
        bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "127.0.0.1:9092",
        )

        _producer = Producer({
            "bootstrap.servers": bootstrap_servers,
        })

    return _producer


def publish_event(event_type, data, key=None):
    event = {
        "event_type": event_type,
        "data": data,
    }

    try:
        producer = get_producer()

        delivery_result = {
            "published": False,
            "partition": None,
            "offset": None,
        }

        def delivery_callback(error, message):
            if error:
                logger.error(
                    "Kafka delivery failed for %s: %s",
                    event_type,
                    error,
                )
                return

            delivery_result["published"] = True
            delivery_result["partition"] = message.partition()
            delivery_result["offset"] = message.offset()

            logger.info(
                "Kafka event published: type=%s partition=%s offset=%s",
                event_type,
                message.partition(),
                message.offset(),
            )

        producer.produce(
            EVENTS_TOPIC,
            key=str(key) if key is not None else None,
            value=json.dumps(event),
            callback=delivery_callback,
        )

        producer.flush(5)

        return delivery_result

    except Exception:
        logger.exception(
            "Failed to publish Kafka event: %s",
            event_type,
        )

        return {
            "published": False,
        }