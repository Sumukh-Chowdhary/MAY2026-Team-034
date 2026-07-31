from app.models import Club, db
from app.models.club import ClubFaculty, ClubMembership
from app.models.user import FacultyProfile
from app.models.events import Event
from sqlalchemy import case
from flask import g

VALID_CLUB_CATEGORIES = {
    "Technology",
    "Academic",
    "Sports",
    "Arts",
    "Cultural",
    "Entrepreneurship",
    "Social Service",
    "General",
}

def serialize_club(club: Club):
    organizers = [
        {
            "id": organizer.user.id,
            "name": (
                organizer.user.student_profile.full_name
                if organizer.user.student_profile
                else organizer.user.faculty_profile.full_name
            ),
        }
        for organizer in club.organizers
    ]

    faculty = [
        {
            "id": advisor.faculty.id,
            "name": advisor.faculty.faculty_profile.full_name,
        }
        for advisor in club.faculty_coordinators
    ]

    return {
        "id": club.id,
        "name": club.club_name,
        "description": club.club_description,
        "category": club.club_category,
        "logo": club.club_logo,
        "status": club.club_status,
        "totalMembers": club.total_members,
        "activeMembers": club.active_members,
        "organizers": organizers,
        "faculty": faculty,
        "createdAt": club.created_at.isoformat(),
    }

def serialize_faculty(member):
    return {
        "id": member.user_id,
        "name": member.full_name,
        "designation": member.designation,
        "department": (
            member.department.name
            if member.department
            else None
        )
    }

def serialize_member(membership):
    return {
        "id": membership.user.id,
        "name": membership.user.student_profile.full_name,
        "email": membership.user.email,
        "membershipRole": membership.membership_role,
        "membershipStatus": membership.membership_status,
        "joinedAt": membership.joined_at.isoformat(),
    }

def serialize_member_profile(membership):
    student = membership.user.student_profile

    return {
        "id": membership.user.id,
        "rollNumber": student.roll_no,
        "name": student.full_name,
        "email": membership.user.email,
        "phoneNumber": student.phone_number,
        "yearOfStudy": student.year_of_study,
        "department": (
            student.department.name
            if student.department
            else None
        ),
        "bio": student.bio,
        "membershipRole": membership.membership_role,
        "membershipStatus": membership.membership_status,
        "joinedAt": membership.joined_at.isoformat(),
    }

def serialize_event(event):
    return {
        "id": event.id,
        "clubId": event.club_id,
        "name": event.event_name,
        "description": event.event_description,
        "status": event.event_status,
        "venueId": event.venue_id,
        "venueName": (
            event.venue.venue_name
            if event.venue
            else None
        ),
        "startDate": event.start_date.isoformat(),
        "endDate": event.end_date.isoformat(),
        "startTime": (
            event.start_time.isoformat()
            if event.start_time
            else None
        ),
        "endTime": (
            event.end_time.isoformat()
            if event.end_time
            else None
        ),
        "capacity": event.capacity,
        "createdBy": event.created_by,
        "createdAt": event.created_at.isoformat(),
        "updatedAt": event.updated_at.isoformat(),
    }

def get_all_clubs():

    query = Club.query

    query = query.order_by(
        case(
            (Club.club_status == "ACTIVE", 0),
            else_=1
        ),
        Club.club_name.asc()
    )
        
    clubs = query.all()

    return [serialize_club(club) for club in clubs]

def get_club_by_id(club_id):
    club = Club.query.get_or_404(club_id)
    return serialize_club(club)

def update_club_status(club_id, status):
    club = Club.query.get_or_404(club_id)

    if status not in ["ACTIVE", "INACTIVE"]:
        raise ValueError("Invalid status")

    club.club_status = status
    db.session.commit()

    return serialize_club(club)

def get_faculty_details():
    faculty = (
        FacultyProfile.query
        .order_by(FacultyProfile.full_name)
        .all()
    )

    return [serialize_faculty(member) for member in faculty]

def create_club(name, category, description, logo, faculty_ids):
    if not name:
        raise ValueError("Club name is required.")

    if not category:
        raise ValueError("Category is required.")

    if not description:
        raise ValueError("Description is required.")

    if not faculty_ids:
        raise ValueError("Select at least one faculty coordinator.")

    if Club.query.filter_by(club_name=name).first():
        raise ValueError("A club with this name already exists.")

    if category not in VALID_CLUB_CATEGORIES:
        raise ValueError("Invalid category.")

    faculty_ids = list(set(faculty_ids))

    faculty_profiles = FacultyProfile.query.filter(
        FacultyProfile.user_id.in_(faculty_ids)
    ).all()

    valid_ids = {faculty.user_id for faculty in faculty_profiles}

    invalid_ids = [
        faculty_id
        for faculty_id in faculty_ids
        if faculty_id not in valid_ids
    ]

    if invalid_ids:
        raise ValueError(
            f"Invalid faculty coordinator(s): {invalid_ids}"
        )

    club = Club(
        club_name=name,
        club_category=category,
        club_description=description,
        club_logo=logo,
        club_status="ACTIVE"
    )

    db.session.add(club)
    db.session.flush()

    for faculty_id in faculty_ids:
        db.session.add(
            ClubFaculty(
                club_id=club.id,
                faculty_id=faculty_id
            )
        )

    db.session.commit()

    return serialize_club(club)

def update_club(club_id, name, category, description, logo, faculty_ids):
    if not name:
        raise ValueError("Club name is required.")

    if not category:
        raise ValueError("Category is required.")

    if not description:
        raise ValueError("Description is required.")

    if not faculty_ids:
        raise ValueError("Select at least one faculty coordinator.")

    club = Club.query.get_or_404(club_id, description="Club not found")

    existing = Club.query.filter(
        db.func.lower(Club.club_name) == name.lower(),
        Club.id != club_id
    ).first()

    if existing:
        raise ValueError("Another club already uses this name.")

    if category not in VALID_CLUB_CATEGORIES:
        raise ValueError("Invalid category.")

    faculty_ids = list(set(faculty_ids))

    faculty_profiles = FacultyProfile.query.filter(
        FacultyProfile.user_id.in_(faculty_ids)
    ).all()

    valid_ids = {faculty.user_id for faculty in faculty_profiles}

    invalid_ids = [
        faculty_id
        for faculty_id in faculty_ids
        if faculty_id not in valid_ids
    ]

    if invalid_ids:
        raise ValueError(
            f"Invalid faculty coordinator(s): {invalid_ids}"
        )

    club.club_name = name
    club.club_category = category
    club.club_description = description
    club.club_logo = logo

    ClubFaculty.query.filter_by(
        club_id=club.id
    ).delete()

    for faculty_id in faculty_ids:
        db.session.add(
            ClubFaculty(
                club_id=club.id,
                faculty_id=faculty_id
            )
        )

    db.session.commit()

    return serialize_club(club)

def archive_club(club_id):

    club = Club.query.get_or_404(club_id, description="Club not found")

    if club.club_status == "INACTIVE":
        raise ValueError("Club is already inactive.")

    club.club_status = "INACTIVE"

    db.session.commit()

    return serialize_club(club)

def get_club_members(club_id, include_inactive=False):
    club = Club.query.get_or_404(club_id, description="Club not found")

    query = ClubMembership.query.filter_by(club_id=club.id)

    if not include_inactive:
        query = query.filter_by(membership_status="ACTIVE")

    members = (
        query
        .order_by(ClubMembership.joined_at)
        .all()
    )

    return [serialize_member(member) for member in members]

def get_club_member(club_id, user_id):
    Club.query.get_or_404(club_id, description="Club not found")

    membership = ClubMembership.query.filter_by(
        club_id=club_id,
        user_id=user_id
    ).first_or_404(description="Member not found")

    return serialize_member_profile(membership)

def deactivate_club_member(club_id, user_id):
    club = Club.query.get_or_404(club_id, description="Club not found")

    membership = ClubMembership.query.filter_by(
        club_id=club_id,
        user_id=user_id
    ).first_or_404(description="Member not found")

    if membership.membership_status == "INACTIVE":
        raise ValueError("Member is already inactive.")

    membership.membership_status = "INACTIVE"

    if club.active_members > 0:
        club.active_members -= 1

    db.session.commit()

    return serialize_member(membership)

def get_club_events(club_id):
    Club.query.get_or_404(club_id, description="Club not found")

    events = (
        Event.query
        .filter_by(club_id=club_id)
        .order_by(Event.start_date.desc())
        .all()
    )

    return [serialize_event(event) for event in events]

def verify_faculty_access(club_id, faculty_id):
    assignment = ClubFaculty.query.filter_by(
        club_id=club_id,
        faculty_id=faculty_id
    ).first()

    if assignment is None:
        raise PermissionError(
            "You are not assigned to this club."
        )

    return assignment

