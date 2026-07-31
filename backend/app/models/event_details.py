from datetime import datetime

from app.models import db


class EventSchedule(db.Model):
    __tablename__ = "event_schedules"

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id"),
        nullable=False
    )

    time = db.Column(
        db.String(30),
        nullable=False
    )

    activity = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "time": self.time,
            "activity": self.activity
        }


class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id"),
        nullable=False
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "date": (
                self.created_at.strftime("%d %b %Y")
                if self.created_at
                else None
            )
        }


class EventRegistration(db.Model):
    __tablename__ = "event_registrations"

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id"),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    registered_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    student = db.relationship(
        "User",
        lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "event_id",
            "student_id",
            name="uq_event_registration"
        ),
    )

    def to_dict(self):
        profile = (
            self.student.student_profile
            if self.student
            else None
        )

        return {
            "id": self.id,
            "name": (
                profile.full_name
                if profile
                else None
            ),
            "registerNumber": (
                profile.roll_no
                if profile
                else None
            ),
            "branch": (
                profile.department.name
                if profile and profile.department
                else None
            )
        }


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id"),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Present"
    )

    marked_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    student = db.relationship(
        "User",
        lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "event_id",
            "student_id",
            name="uq_event_attendance"
        ),
    )

    def to_dict(self):
        profile = (
            self.student.student_profile
            if self.student
            else None
        )

        return {
            "id": self.id,
            "name": (
                profile.full_name
                if profile
                else None
            ),
            "registerNumber": (
                profile.roll_no
                if profile
                else None
            ),
            "status": self.status
        }