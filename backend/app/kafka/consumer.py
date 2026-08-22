import json
import logging
import os

from confluent_kafka import Consumer

from app import create_app
from app.models import db
from app.models.events import Event, EventRegistration
from app.models.kafka_event_log import KafkaEventLog
from app.services.notification_service import NotificationService
from app.kafka.events import (
    EVENTS_TOPIC,
    EVENT_COMPLETED,
    PARTICIPANT_PROGRESS_UPDATED,
    RESULTS_PUBLISHED,
    WINNERS_ANNOUNCED,
    REQUEST_APPROVED,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_event_completed(data):
    event_id = data.get("event_id")

    if not event_id:
        logger.warning("EVENT_COMPLETED received without event_id")
        return

    event = db.session.get(Event, event_id)

    if not event:
        logger.warning("Event %s not found", event_id)
        return

    registrations = EventRegistration.query.filter(
        EventRegistration.event_id == event_id,
        EventRegistration.registration_status.in_([
            "REGISTERED",
            "ATTENDED",
        ])
    ).all()

    logger.info(
        "Processing completion notifications for event %s (%s participants)",
        event_id,
        len(registrations),
    )

    for registration in registrations:
        NotificationService.create(
            user_id=registration.user_id,
            title="Event Completed",
            message=(
                f"The event '{event.event_name}' has been completed. "
                "Thank you for participating!"
            ),
            notification_type="EVENT_COMPLETED",
            entity_type="EVENT",
            entity_id=event.id,
            context=event.club.club_name if event.club else "General Event",
            reference_url=f"/student/events/{event.id}",
        )


def process_participant_progress_updated(data):
    event_id = data.get("event_id")
    session_name = data.get("session_name")
    finalist_round = data.get("finalist_round", False)

    shortlisted_user_ids = data.get("shortlisted_user_ids", [])
    eliminated_user_ids = data.get("eliminated_user_ids", [])
    elimination_reason = data.get(
        "elimination_reason",
        "Not shortlisted"
    )

    if not event_id:
        logger.warning(
            "PARTICIPANT_PROGRESS_UPDATED received without event_id"
        )
        return

    event = db.session.get(Event, event_id)

    if not event:
        logger.warning("Event %s not found", event_id)
        return

    logger.info(
        "Processing participant progress for event %s | "
        "shortlisted=%s | eliminated=%s",
        event_id,
        len(shortlisted_user_ids),
        len(eliminated_user_ids),
    )

    # Notify shortlisted participants.
    for user_id in shortlisted_user_ids:
        if finalist_round:
            NotificationService.create(
                user_id=user_id,
                title="You are a Finalist!",
                message=(
                    f"Congratulations! You have reached the final stage "
                    f"of '{event.event_name}'."
                ),
                notification_type="EVENT_FINALIST",
                entity_type="EVENT",
                entity_id=event.id,
                context=session_name,
                reference_url=f"/student/events/{event.id}",
            )
        else:
            NotificationService.create(
                user_id=user_id,
                title="You have been shortlisted!",
                message=(
                    f"Congratulations! You have been shortlisted in "
                    f"'{session_name}' for '{event.event_name}'."
                ),
                notification_type="EVENT_SHORTLISTED",
                entity_type="EVENT",
                entity_id=event.id,
                context=session_name,
                reference_url=f"/student/events/{event.id}",
            )

    # Notify eliminated participants.
    for user_id in eliminated_user_ids:
        NotificationService.create(
            user_id=user_id,
            title="Participant Progress Update",
            message=(
                f"You were not shortlisted in '{session_name}' "
                f"for '{event.event_name}'. "
                f"Reason: {elimination_reason}"
            ),
            notification_type="EVENT_ELIMINATED",
            entity_type="EVENT",
            entity_id=event.id,
            context=session_name,
            reference_url=f"/student/events/{event.id}",
        )


def process_results_published(data):
    event_id = data.get("event_id")
    title = data.get("title")

    if not event_id:
        logger.warning("RESULTS_PUBLISHED received without event_id")
        return

    event = db.session.get(Event, event_id)

    if not event:
        logger.warning("Event %s not found", event_id)
        return

    registrations = EventRegistration.query.filter(
        EventRegistration.event_id == event_id,
        EventRegistration.registration_status.in_([
            "REGISTERED",
            "ATTENDED",
        ])
    ).all()

    logger.info(
        "Processing results notifications for event %s (%s participants)",
        event_id,
        len(registrations),
    )

    for registration in registrations:
        NotificationService.create(
            user_id=registration.user_id,
            title=title or "Results Announced",
            message=(
                f"Results for '{event.event_name}' have been published. "
                "Open the event to view the announcement."
            ),
            notification_type="RESULTS_PUBLISHED",
            entity_type="EVENT",
            entity_id=event.id,
            context=event.club.club_name if event.club else "General Event",
            reference_url=f"/student/events/{event.id}",
        )


def process_winners_announced(data):
    event_id = data.get("event_id")

    if not event_id:
        logger.warning("WINNERS_ANNOUNCED received without event_id")
        return

    event = db.session.get(Event, event_id)

    if not event:
        logger.warning("Event %s not found", event_id)
        return

    registrations = EventRegistration.query.filter(
        EventRegistration.event_id == event_id,
        EventRegistration.registration_status.in_([
            "REGISTERED",
            "ATTENDED",
        ])
    ).all()

    logger.info(
        "Processing winners announced notifications for event %s (%s participants)",
        event_id,
        len(registrations),
    )

    for registration in registrations:
        NotificationService.create(
            user_id=registration.user_id,
            title="Winners Announced!",
            message=(
                f"Winners have been announced for '{event.event_name}'."
            ),
            notification_type="WINNERS_ANNOUNCED",
            entity_type="EVENT",
            entity_id=event.id,
            context=event.club.club_name if event.club else "General Event",
            reference_url=f"/student/events/{event.id}",
        )


def process_request_approved(data):
    ticket_id = data.get("ticket_id")
    creator_id = data.get("creator_id")
    title = data.get("title")

    if not creator_id:
        logger.warning("REQUEST_APPROVED received without creator_id")
        return

    NotificationService.create(
        user_id=creator_id,
        title="Request Approved",
        message=f"Your request '{title or 'Action Ticket'}' has been approved.",
        notification_type="REQUEST_APPROVED",
        entity_type="TICKET",
        entity_id=ticket_id,
        reference_url="/notifications",
    )


def process_kafka_event(event, partition, offset):
    existing = KafkaEventLog.query.filter_by(
        kafka_partition=partition,
        kafka_offset=offset,
    ).first()

    if existing:
        logger.info(
            "Kafka event already processed | partition=%s | offset=%s",
            partition,
            offset,
        )
        return

    event_type = event.get("event_type")
    data = event.get("data", {})

    if event_type == EVENT_COMPLETED:
        process_event_completed(data)

    elif event_type == PARTICIPANT_PROGRESS_UPDATED:
        process_participant_progress_updated(data)

    elif event_type == RESULTS_PUBLISHED:
        process_results_published(data)

    elif event_type == WINNERS_ANNOUNCED:
        process_winners_announced(data)

    elif event_type == REQUEST_APPROVED:
        process_request_approved(data)

    else:
        logger.warning(
            "Unknown Kafka event type: %s",
            event_type,
        )

    # Record the event only after processing succeeds.
    log = KafkaEventLog(
        event_type=event_type,
        event_id=data.get("event_id"),
        kafka_partition=partition,
        kafka_offset=offset,
    )

    db.session.add(log)
    db.session.commit()

    logger.info(
        "Kafka event processed | type=%s | partition=%s | offset=%s",
        event_type,
        partition,
        offset,
    )


def run_consumer():
    bootstrap_servers = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "127.0.0.1:9092",
    )

    app = create_app()

    consumer = Consumer({
        "bootstrap.servers": bootstrap_servers,
        "group.id": "allclub-notification-consumer",
        "auto.offset.reset": "latest",
        "enable.auto.commit": True,
    })

    consumer.subscribe([EVENTS_TOPIC])

    logger.info("AllClub Kafka consumer started")

    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                continue

            if message.error():
                logger.error(
                    "Kafka error: %s",
                    message.error(),
                )
                continue

            event = json.loads(
                message.value().decode("utf-8")
            )

            with app.app_context():
                process_kafka_event(
                    event,
                    message.partition(),
                    message.offset(),
                )

    except KeyboardInterrupt:
        logger.info("Kafka consumer stopped")

    finally:
        consumer.close()


if __name__ == "__main__":
    run_consumer()