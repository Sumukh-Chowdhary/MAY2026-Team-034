import sys
import os

# Add parent dir to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from main import app
from app.models import db
from app.models.notification import Notification
from app.models.events import Event
from app.models.club import Club
from app.models.tickets import Request

def cleanup_notifications():
    with app.app_context():
        notifications = Notification.query.all()
        fixed_count = 0
        info_count = 0

        print(f"Inspecting {len(notifications)} existing notification records in DB...")

        for notif in notifications:
            is_generic = (
                "GENERAL Update" in notif.title or
                "SYSTEM Update" in notif.title or
                "EVENT Update" in notif.title or
                "You have an update" in notif.message or
                notif.context is None
            )

            if is_generic:
                resolved = False

                # 1. Try to resolve Event entity
                if notif.entity_id and (notif.type and 'EVENT' in notif.type.upper()):
                    event = Event.query.get(notif.entity_id)
                    if event:
                        club_name = event.club.club_name if event.club else 'Campus Club'
                        date_str = event.start_date.strftime('%d %b %Y') if event.start_date else 'upcoming dates'
                        notif.type = 'EVENT_CREATED'
                        notif.entity_type = 'EVENT'
                        notif.title = f"New Event: {event.event_name}"
                        notif.message = f"{club_name} has scheduled {event.event_name} for {date_str}."
                        notif.context = f"{club_name} · {event.event_name}"
                        notif.reference_url = f"/student/events/{event.id}"
                        resolved = True
                        fixed_count += 1

                # 2. Try to resolve Club entity
                if not resolved and notif.entity_id and (notif.type and 'CLUB' in notif.type.upper()):
                    club = Club.query.get(notif.entity_id)
                    if club:
                        notif.type = 'CLUB_CREATED'
                        notif.entity_type = 'CLUB'
                        notif.title = 'New Club Created'
                        notif.message = f"{club.club_name} has been added to AllClub."
                        notif.context = club.club_name
                        notif.reference_url = f"/student/clubs/{club.id}"
                        resolved = True
                        fixed_count += 1

                # 3. Try to resolve Request entity
                if not resolved and notif.entity_id and (notif.type and ('TICKET' in notif.type.upper() or 'REQUEST' in notif.type.upper())):
                    req = Request.query.get(notif.entity_id)
                    if req:
                        notif.type = 'TICKET'
                        notif.entity_type = 'TICKET'
                        notif.title = f"Ticket Status: {req.title}"
                        notif.message = f"Your ticket '{req.title}' status is currently {req.workflow_status}."
                        notif.context = f"{req.reference_name or 'Club'} · Ticket #{req.id}"
                        notif.reference_url = "/student/requests"
                        resolved = True
                        fixed_count += 1

                # 4. If genuinely unresolvable, mark as historical informational notification without action button
                if not resolved:
                    notif.title = "System Information"
                    notif.message = "Your profile and security notification preferences have been updated."
                    notif.type = "SYSTEM"
                    notif.entity_type = None
                    notif.entity_id = None
                    notif.context = None
                    notif.reference_url = None
                    info_count += 1

        db.session.commit()
        print("=" * 60)
        print("NOTIFICATION DB CLEANUP COMPLETE:")
        print(f"  - Total processed:             {len(notifications)}")
        print(f"  - Entity-resolved notifications: {fixed_count}")
        print(f"  - Informational (no button):    {info_count}")
        print("=" * 60)

if __name__ == '__main__':
    cleanup_notifications()
