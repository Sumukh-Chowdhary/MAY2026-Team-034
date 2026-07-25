from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.user import (  # noqa: E402
    Role, Department, Permission, RolePermission,
    User, StudentProfile, FacultyProfile, TokenBlocklist
)

__all__ = [
    'db',
    'Role',
    'Department',
    'Permission',
    'RolePermission',
    'User',
    'StudentProfile',
    'FacultyProfile',
    'TokenBlocklist'
]
