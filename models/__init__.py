from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.user import (  # noqa: E402
    Role, Department, Permission, RolePermission,
    User, StudentProfile, FacultyProfile, TokenBlocklist
)

from app.models.club import Club

__all__ = [
    'db',
    'Role',
    'Department',
    'Permission',
    'RolePermission',
    'User',
    'StudentProfile',
    'FacultyProfile',
    'TokenBlocklist',
    'Club'
]
