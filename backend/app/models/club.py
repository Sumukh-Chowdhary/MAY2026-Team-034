from datetime import datetime
from app.models import db

class Club(db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(100), unique=True, nullable=False)
    club_category = db.Column(db.String(50), nullable=False)
    club_description = db.Column(db.Text, nullable=False)
    club_logo = db.Column(db.String(255), nullable=True)
    club_status = db.Column(db.String(20),nullable=False,default="ACTIVE")
    total_members = db.Column(db.Integer,nullable=False,default=0)
    active_members = db.Column(db.Integer,nullable=False,default=0)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)

    memberships = db.relationship("ClubMembership",backref="club",lazy=True,cascade="all, delete-orphan")
    organizers = db.relationship("ClubOrganizer",backref="club",lazy=True,cascade="all, delete-orphan")
    faculty_coordinators = db.relationship("ClubFaculty",backref="club",lazy=True,cascade="all, delete-orphan")
    #events = db.relationship("Event",backref="club",lazy=True,cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "clubName": self.club_name,
            "category": self.club_category,
            "description": self.club_description,
            "logo": self.club_logo,
            "status": self.club_status,
            "totalMembers": self.total_members,
            "activeMembers": self.active_members,
            "createdAt": (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }

class ClubMembership(db.Model):
    __tablename__ = "club_memberships"

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer,db.ForeignKey("clubs.id"),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    membership_role = db.Column(db.String(30),nullable=False,default="MEMBER")
    membership_status = db.Column(db.String(20),nullable=False,default="ACTIVE")
    joined_at = db.Column(db.DateTime,default=datetime.utcnow)

    user = db.relationship("User", lazy=True)

    __table_args__ = (db.UniqueConstraint("club_id","user_id",name="uq_club_member"),)

class ClubOrganizer(db.Model):
    __tablename__ = "club_organizers"

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer,db.ForeignKey("clubs.id"),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    organizer_role = db.Column(db.String(30),nullable=False,default="ORGANIZER")
    assigned_at = db.Column(db.DateTime,default=datetime.utcnow)

    user = db.relationship("User", lazy=True)

    __table_args__ = (db.UniqueConstraint("club_id","user_id",name="uq_club_organizer"),)

class ClubFaculty(db.Model):
    __tablename__ = "club_faculty"

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer,db.ForeignKey("clubs.id"),nullable=False)
    faculty_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    faculty_role = db.Column(db.String(50),nullable=False,default="FACULTY_COORDINATOR")
    assigned_at = db.Column(db.DateTime,default=datetime.utcnow)

    faculty = db.relationship("User", lazy=True)

    __table_args__ = (db.UniqueConstraint("club_id","faculty_id",name="uq_club_faculty"),)
