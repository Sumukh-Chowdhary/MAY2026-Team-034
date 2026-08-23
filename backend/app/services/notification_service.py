from app.models import db
from app.models.notification import Notification
from app.extensions import socketio

class NotificationService:
    @staticmethod
    def create(user_id, title, message, notification_type, entity_id=None, reference_url=None, entity_type=None, actor_id=None, context=None):
        """Creates a notification with rich metadata and emits a socket event."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            context=context,
            reference_url=reference_url
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Emit real-time update
        room = f"user_{user_id}"
        socketio.emit("new_notification", notification.to_dict(), room=room)
        
        return notification

    @staticmethod
    def get_user_notifications(user_id, limit=15):
        return Notification.query.filter_by(user_id=user_id).order_by(
            Notification.is_read.asc(),
            Notification.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def unread_count(user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def mark_read(notification_id, user_id):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
        return notification

    @staticmethod
    def mark_all_read(user_id):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
        db.session.commit()

    @staticmethod
    def notify_ticket_created(creator_id, ticket_id, approver_ids=None, ticket_title=None, club_name=None):
        ctx = f"{club_name} · Ticket #{ticket_id}" if club_name else f"Ticket #{ticket_id}"
        desc = f"Your ticket #{ticket_id}" + (f" ({ticket_title})" if ticket_title else "") + " has been submitted."
        
        # Notify Creator
        NotificationService.create(
            user_id=creator_id,
            title="Ticket Created",
            message=desc,
            notification_type="TICKET",
            entity_type="TICKET",
            entity_id=ticket_id,
            context=ctx,
            reference_url=f"/student/requests"
        )
        
        # Notify Approvers
        if approver_ids:
            for approver_id in approver_ids:
                NotificationService.create(
                    user_id=approver_id,
                    title="New Ticket Assigned",
                    message=f"You have been assigned to review Ticket #{ticket_id}" + (f" for {club_name}." if club_name else "."),
                    notification_type="TICKET",
                    entity_type="TICKET",
                    entity_id=ticket_id,
                    context=ctx,
                    reference_url=f"/faculty/requests"
                )

    @staticmethod
    def notify_ticket_approved(creator_id, ticket_id, approver_name, request_title=None, club_name=None, actor_id=None):
        ctx = f"{club_name} · Request" if club_name else f"Ticket #{ticket_id}"
        msg = f"{approver_name} approved your request" + (f" for {request_title}." if request_title else f" #{ticket_id}.")
        
        NotificationService.create(
            user_id=creator_id,
            title="Request Approved",
            message=msg,
            notification_type="TICKET",
            entity_type="TICKET",
            entity_id=ticket_id,
            actor_id=actor_id,
            context=ctx,
            reference_url=f"/student/requests"
        )

    @staticmethod
    def notify_ticket_rejected(creator_id, ticket_id, approver_name, request_title=None, club_name=None, actor_id=None):
        ctx = f"{club_name} · Request" if club_name else f"Ticket #{ticket_id}"
        msg = f"{approver_name} rejected your request" + (f" for {request_title}." if request_title else f" #{ticket_id}.")
        
        NotificationService.create(
            user_id=creator_id,
            title="Ticket Rejected",
            message=msg,
            notification_type="TICKET",
            entity_type="TICKET",
            entity_id=ticket_id,
            actor_id=actor_id,
            context=ctx,
            reference_url=f"/student/requests"
        )

    @staticmethod
    def notify_ticket_fully_approved(creator_id, ticket_id, request_title=None, club_name=None):
        ctx = f"{club_name} · Request" if club_name else f"Ticket #{ticket_id}"
        msg = f"Your request" + (f" for {request_title}" if request_title else f" #{ticket_id}") + " has been fully approved."
        
        NotificationService.create(
            user_id=creator_id,
            title="Ticket Fully Approved",
            message=msg,
            notification_type="TICKET",
            entity_type="TICKET",
            entity_id=ticket_id,
            context=ctx,
            reference_url=f"/student/requests"
        )

    @staticmethod
    def notify_ticket_closed(creator_id, ticket_id, request_title=None):
        NotificationService.create(
            user_id=creator_id,
            title="Ticket Closed",
            message=f"Your ticket #{ticket_id}" + (f" ({request_title})" if request_title else "") + " has been closed.",
            notification_type="TICKET",
            entity_type="TICKET",
            entity_id=ticket_id,
            context=f"Ticket #{ticket_id}",
            reference_url=f"/student/requests"
        )

    @staticmethod
    def notify_club_created(creator_id, club_name, club_id):
        NotificationService.create(
            user_id=creator_id,
            title="New Club Created",
            message=f"{club_name} has been added to AllClub.",
            notification_type="CLUB_CREATED",
            entity_type="CLUB",
            entity_id=club_id,
            context=club_name,
            reference_url=f"/student/clubs/{club_id}"
        )

    @staticmethod
    def notify_role_assigned(user_id, role_title, club_name):
        ctx = f"{club_name}" if club_name else "Role Assignment"
        NotificationService.create(
            user_id=user_id,
            title=f"{role_title} Role Assigned",
            message=f"You have been assigned as {role_title} for {club_name or 'the club'}.",
            notification_type="ROLE_ASSIGNED",
            entity_type="ROLE",
            context=ctx,
            reference_url="/student/roles"
        )

    @staticmethod
    def notify_event_created(event_id, event_name, club_name, target_user_ids, scheduled_date=None):
        ctx = f"{club_name or 'Campus Club'} · {event_name}"
        msg = f"{club_name or 'AI Club'} has created a new event scheduled for {scheduled_date or 'upcoming dates'}."
        for uid in set(target_user_ids or []):
            NotificationService.create(
                user_id=uid,
                title=f"New Event: {event_name}",
                message=msg,
                notification_type="EVENT_CREATED",
                entity_type="EVENT",
                entity_id=event_id,
                context=ctx,
                reference_url=f"/student/events/{event_id}"
            )

    @staticmethod
    def notify_event_registered(event_id, event_name, club_name=None, user_id=None):
        if user_id is None and isinstance(club_name, int):
            user_id = club_name
            club_name = None
        ctx = f"{club_name or 'Club'} · {event_name}"
        NotificationService.create(
            user_id=user_id,
            title="Registration Confirmed",
            message=f"You are registered for {event_name}.",
            notification_type="EVENT_REGISTERED",
            entity_type="EVENT",
            entity_id=event_id,
            context=ctx,
            reference_url=f"/student/events/{event_id}"
        )

    @staticmethod
    def notify_event_schedule_changed(event_id, event_name, *args):
        # args can be (club_name, update_details, target_user_ids) or (update_details, target_user_ids)
        if len(args) == 2:
            club_name = None
            update_details, target_user_ids = args
        elif len(args) >= 3:
            club_name, update_details, target_user_ids = args[0], args[1], args[2]
        else:
            club_name, update_details, target_user_ids = None, "", []
        ctx = f"{club_name or 'Club'} · {event_name}"
        msg = f"The {event_name} schedule has been updated: {update_details}."
        for uid in set(target_user_ids or []):
            NotificationService.create(
                user_id=uid,
                title="Event Schedule Updated",
                message=msg,
                notification_type="EVENT_SCHEDULE_CHANGED",
                entity_type="EVENT",
                entity_id=event_id,
                context=ctx,
                reference_url=f"/student/events/{event_id}"
            )

    @staticmethod
    def notify_event_venue_changed(event_id, event_name, *args):
        # args can be (club_name, venue_name, target_user_ids) or (venue_name, target_user_ids)
        if len(args) == 2:
            club_name = None
            venue_name, target_user_ids = args
        elif len(args) >= 3:
            club_name, venue_name, target_user_ids = args[0], args[1], args[2]
        else:
            club_name, venue_name, target_user_ids = None, "", []
        ctx = f"{club_name or 'Club'} · {event_name}"
        for uid in set(target_user_ids or []):
            NotificationService.create(
                user_id=uid,
                title="Venue Updated",
                message=f"{event_name} will now be held at {venue_name}.",
                notification_type="EVENT_VENUE_CHANGED",
                entity_type="EVENT",
                entity_id=event_id,
                context=ctx,
                reference_url=f"/student/events/{event_id}"
            )

    @staticmethod
    def notify_event_announcement(event_id, event_name, club_name, title, message, target_user_ids):
        ctx = f"{club_name or 'Club'} · {event_name}"
        for uid in set(target_user_ids or []):
            NotificationService.create(
                user_id=uid,
                title="New Event Announcement",
                message=f"{club_name or 'Club'} has published an announcement for {event_name}: {title}",
                notification_type="EVENT_ANNOUNCEMENT",
                entity_type="EVENT",
                entity_id=event_id,
                context=ctx,
                reference_url=f"/student/events/{event_id}"
            )

    @staticmethod
    def notify_volunteer_approved(user_id, event_id, event_name, club_name, role_name, start_date=None, end_date=None):
        ctx = f"{club_name or 'Club'} · {event_name}"
        date_str = f" from {start_date} to {end_date}" if (start_date and end_date) else ""
        msg = f"You have been selected as {role_name} volunteer for {event_name}{date_str}."
        NotificationService.create(
            user_id=user_id,
            title="Volunteer Application Approved",
            message=msg,
            notification_type="VOLUNTEER_APPROVED",
            entity_type="VOLUNTEER",
            entity_id=event_id,
            context=ctx,
            reference_url="/student/roles"
        )

    @staticmethod
    def notify_volunteer_rejected(user_id, event_id, event_name, club_name, role_name):
        ctx = f"{club_name or 'Club'} · {event_name}"
        msg = f"Your volunteer application for {role_name} at {event_name} was not accepted."
        NotificationService.create(
            user_id=user_id,
            title="Volunteer Application Update",
            message=msg,
            notification_type="VOLUNTEER_REJECTED",
            entity_type="VOLUNTEER",
            entity_id=event_id,
            context=ctx,
            reference_url="/student/roles"
        )

    @staticmethod
    def notify_attendance_updated(user_id, event_id, event_name, club_name, round_name, status):
        ctx = f"{club_name or 'Club'} · {event_name} · {round_name or 'Session'}"
        msg = f"Your attendance for {round_name or 'Round'} of {event_name} has been recorded as {status}."
        NotificationService.create(
            user_id=user_id,
            title="Attendance Updated",
            message=msg,
            notification_type="EVENT_ATTENDANCE",
            entity_type="EVENT",
            entity_id=event_id,
            context=ctx,
            reference_url=f"/student/events/{event_id}"
        )

    @staticmethod
    def notify_participant_shortlisted(event_id, event_name, *args):
        # args can be (club_name, user_id, round_name) or (user_id, round_name)
        if len(args) == 2:
            club_name = None
            user_id, round_name = args
        elif len(args) >= 3:
            club_name, user_id, round_name = args[0], args[1], args[2]
        else:
            club_name, user_id, round_name = None, None, "Next Round"
        ctx = f"{club_name or 'Club'} · {event_name}"
        NotificationService.create(
            user_id=user_id,
            title="You're Shortlisted! 🎉",
            message=f"You have advanced to {round_name} of {event_name}.",
            notification_type="EVENT_SHORTLISTED",
            entity_type="EVENT",
            entity_id=event_id,
            context=ctx,
            reference_url=f"/student/events/{event_id}"
        )

    @staticmethod
    def notify_participant_eliminated(event_id, event_name, *args):
        # args can be (club_name, user_id, round_name, reason) or (user_id, round_name, reason)
        if len(args) == 3:
            club_name = None
            user_id, round_name, reason = args
        elif len(args) >= 4:
            club_name, user_id, round_name, reason = args[0], args[1], args[2], args[3]
        else:
            club_name, user_id, round_name, reason = None, args[0] if args else None, "Round", ""
        ctx = f"{club_name or 'Club'} · {event_name}"
        msg = f"You have been eliminated from {round_name} of {event_name}." + (f" Reason: {reason}" if reason else "")
        NotificationService.create(
            user_id=user_id,
            title="Event Update",
            message=msg,
            notification_type="EVENT_ELIMINATED",
            entity_type="EVENT",
            entity_id=event_id,
            context=ctx,
            reference_url=f"/student/events/{event_id}"
        )

    @staticmethod
    def notify_participant_finalist(event_id, event_name, *args):
        # args can be (club_name, user_id) or (user_id,)
        if len(args) == 1:
            club_name = None
            user_id = args[0]
        elif len(args) >= 2:
            club_name, user_id = args[0], args[1]
        else:
            club_name, user_id = None, None
        ctx = f"{club_name or 'Club'} · {event_name}"
        NotificationService.create(
            user_id=user_id,
            title="You're a Finalist! 🌟",
            message=f"Congratulations! You have reached the Final round of {event_name}.",
            notification_type="EVENT_FINALIST",
            entity_type="EVENT",
            entity_id=event_id,
            context=ctx,
            reference_url=f"/student/events/{event_id}"
        )

    @staticmethod
    def notify_participant_winner(event_id, event_name, *args):
        # args can be (club_name, user_id, role_name) or (user_id, role_name)
        if len(args) == 2:
            club_name = None
            user_id, role_name = args
        elif len(args) >= 3:
            club_name, user_id, role_name = args[0], args[1], args[2]
        else:
            club_name, user_id, role_name = None, None, "Winner"
        ctx = f"{club_name or 'Club'} · {event_name}"
        title = "Congratulations! 🏆"
        message = f"Results for {event_name} have been published. You finished as {role_name}!"
        NotificationService.create(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="EVENT_WINNER",
            entity_type="EVENT",
            entity_id=event_id,
            context=ctx,
            reference_url=f"/student/events/{event_id}"
        )

    @staticmethod
    def notify_event_cancelled(event_id, event_name, target_user_ids, club_name=None):
        ctx = f"{club_name or 'Club'} · {event_name}"
        for uid in set(target_user_ids or []):
            NotificationService.create(
                user_id=uid,
                title="Event Cancelled",
                message=f"{event_name} has been cancelled.",
                notification_type="EVENT_CANCELLED",
                entity_type="EVENT",
                entity_id=event_id,
                context=ctx,
                reference_url="/student/events"
            )

    @staticmethod
    def notify_club_status_changed(club_id, club_name, status, target_user_ids):
        for uid in set(target_user_ids or []):
            NotificationService.create(
                user_id=uid,
                title=f"Club {status.capitalize()}",
                message=f"{club_name} status has been changed to {status}.",
                notification_type="CLUB_UPDATED",
                entity_type="CLUB",
                entity_id=club_id,
                context=club_name,
                reference_url=f"/student/clubs/{club_id}"
            )

    @staticmethod
    def notify_budget_approved(user_id, request_id, club_name, amount):
        ctx = f"{club_name or 'Club'} · Budget Request"
        amt_str = f"₹{amount:,.0f}" if isinstance(amount, (int, float)) else str(amount)
        msg = f"Your {club_name or 'Club'} budget request for {amt_str} has been approved."
        NotificationService.create(
            user_id=user_id,
            title="Budget Request Approved",
            message=msg,
            notification_type="BUDGET_APPROVED",
            entity_type="BUDGET",
            entity_id=request_id,
            context=ctx,
            reference_url=f"/student/requests"
        )

    @staticmethod
    def notify_budget_rejected(user_id, request_id, club_name, amount, approver_name=None):
        ctx = f"{club_name or 'Club'} · Budget Request"
        amt_str = f"₹{amount:,.0f}" if isinstance(amount, (int, float)) else str(amount)
        actor_str = f"{approver_name} " if approver_name else ""
        msg = f"{actor_str}Your {club_name or 'Club'} budget request for {amt_str} was not approved."
        NotificationService.create(
            user_id=user_id,
            title="Budget Request Rejected",
            message=msg,
            notification_type="BUDGET_REJECTED",
            entity_type="BUDGET",
            entity_id=request_id,
            context=ctx,
            reference_url=f"/student/requests"
        )