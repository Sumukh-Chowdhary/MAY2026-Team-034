from datetime import datetime
from app.models import db


class Club(db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)

    club_name = db.Column(db.String(100), unique=True, nullable=False)
    club_description = db.Column(db.Text, nullable=False)
    club_category = db.Column(db.String(50), nullable=False)

    club_logo = db.Column(db.String(255), nullable=True)
    club_status = db.Column(
        db.String(20),
        nullable=False,
        default="ACTIVE"
    )

    organizer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    faculty_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    organizer = db.relationship(
        "User",
        foreign_keys=[organizer_id],
        lazy=True
    )

    faculty = db.relationship(
        "User",
        foreign_keys=[faculty_id],
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.club_name,
            "description": self.club_description,
            "category": self.club_category,
            "logo": self.club_logo,
            "status": self.club_status,
            "organizerId": self.organizer_id,
            "facultyId": self.faculty_id,
            "members": 0,          # Updated once Membership model is added
            "createdAt": (
                self.created_at.isoformat()
                if self.created_at else None
            ),
            "updatedAt": (
                self.updated_at.isoformat()
                if self.updated_at else None
            ),
        }

    def __repr__(self):
        return f"<Club {self.club_name}>"