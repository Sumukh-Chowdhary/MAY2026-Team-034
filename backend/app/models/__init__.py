from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.user import ( 
    Role, Department, User, StudentProfile, FacultyProfile, TokenBlocklist
)

from app.models.club import (
    Club,ClubFaculty,ClubMembership,ClubOrganizer
)

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
    'ClubOrganizer'
]
