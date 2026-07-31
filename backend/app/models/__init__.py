from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.user import ( 
    Role, Department, User, StudentProfile, FacultyProfile, TokenBlocklist
)

from app.models.club import (
    Club,ClubFaculty,ClubMembership,ClubOrganizer
)

from app.models.tickets import (
    Request, RequestApproval, AssignmentTicket,
    ActionTicket, ActionTicketApproval, TicketAudit
)

from app.models.club import Club

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

    'Request',
    'RequestApproval',
    'AssignmentTicket',
    'ActionTicket',
    'ActionTicketApproval',
    'TicketAudit'
]
