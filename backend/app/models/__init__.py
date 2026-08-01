from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.user import (
    Role, Department, User, StudentProfile, FacultyProfile, TokenBlocklist
)

from app.models.club import (
    Club, ClubFaculty, ClubMembership, ClubOrganizer
)

from app.models.tickets import (
    Request, RequestApproval, AssignmentTicket,
    ActionTicket, ActionTicketApproval, TicketAudit
)

from app.models.events import (
    Venue, Event,
    EventScheduleItem, EventAnnouncement, EventRegistration,
    EventAttendance, EventPrize, EventOrganizer, EventVolunteer
)

from app.models.tickets import (
    Request, RequestApproval, AssignmentTicket,
    ActionTicket, ActionTicketApproval, TicketAudit
)

from app.models.events import (
    Venue, Event,
    EventScheduleItem, EventAnnouncement, EventRegistration,
    EventAttendance, EventPrize, EventOrganizer, EventVolunteer
)

from app.models.notification import Notification

__all__ = [
    'db',
    'Role',
    'Department',
    'User',
    'StudentProfile',
    'FacultyProfile',
    'TokenBlocklist',
    'Club',
    'ClubFaculty',
    'ClubMembership',
    'ClubOrganizer',
    'Venue',
    'Event',
    'EventScheduleItem',
    'EventAnnouncement',
    'EventRegistration',
    'EventAttendance',
    'EventPrize',
    'EventOrganizer',
    'EventOrganizer',
    'EventVolunteer',
    'ClubOrganizer',

    'Request',
    'RequestApproval',
    'AssignmentTicket',
    'ActionTicket',
    'ActionTicketApproval',
    'TicketAudit',
    
    'Notification'
]
