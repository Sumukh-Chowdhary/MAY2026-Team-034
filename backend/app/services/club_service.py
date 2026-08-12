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
    # Calculate live current active members (User.account_status == 'ACTIVE' and membership_status == 'ACTIVE')
    active_mems = [
        m for m in club.memberships 
        if m.membership_status == 'ACTIVE' and m.user and m.user.account_status == 'ACTIVE'
    ]
    legacy_mems = [
        m for m in club.memberships 
        if (m.user and m.user.account_status == 'LEGACY') or m.membership_status in ['LEGACY', 'GRADUATED']
    ]

    active_count = len(active_mems)
    legacy_count = len(legacy_mems)

    organizers = [
        {
            "id": organizer.user.id,
            "name": (
                organizer.user.student_profile.full_name
                if organizer.user and organizer.user.student_profile
                else (organizer.user.faculty_profile.full_name if organizer.user and organizer.user.faculty_profile else 'Organizer')
            ),
        }
        for organizer in club.organizers
        if organizer.user and organizer.user.account_status == 'ACTIVE'
    ]

    faculty = [
        {
            "id": advisor.faculty.id,
            "name": advisor.faculty.faculty_profile.full_name if (advisor.faculty and hasattr(advisor.faculty, 'faculty_profile') and advisor.faculty.faculty_profile) else 'Faculty Advisor',
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
        "totalMembers": active_count,
        "activeMembers": active_count,
        "legacyMembers": legacy_count,
        "organizers": organizers,
        "faculty": faculty,
        "createdAt": club.created_at.isoformat() if club.created_at else None,
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
    student = membership.user.student_profile if (membership.user and membership.user.student_profile) else None
    user_status = membership.user.account_status if membership.user else 'ACTIVE'
    is_legacy = (user_status == 'LEGACY')
    reg_id = (student.registration_id or student.roll_no) if student else None

    return {
        "id": membership.user.id,
        "userId": membership.user.id,
        "name": student.full_name if student else membership.user.email.split('@')[0],
        "email": membership.user.email,
        "rollNumber": reg_id,
        "registerNumber": reg_id,
        "registrationId": reg_id,
        "department": (student.department.name if (student and student.department) else None),
        "branchCode": getattr(student, 'branch_code', None) if student else None,
        "batchYear": getattr(student, 'batch_year', None) if student else None,
        "graduationYear": getattr(student, 'graduation_year', None) if student else None,
        "membershipRole": membership.membership_role,
        "membershipStatus": membership.membership_status,
        "userStatus": user_status,
        "isLegacy": is_legacy,
        "avatarStyle": getattr(student, 'avatar_style', 'adventurer') if student else 'adventurer',
        "avatarSeed": getattr(student, 'avatar_seed', None) if student else membership.user.email,
        "joinedAt": membership.joined_at.isoformat() if membership.joined_at else None,
        "leftAt": membership.left_at.isoformat() if (hasattr(membership, 'left_at') and membership.left_at) else None
    }

def serialize_member_profile(membership):
    student = membership.user.student_profile if (membership.user and membership.user.student_profile) else None
    user_status = membership.user.account_status if membership.user else 'ACTIVE'
    is_legacy = (user_status == 'LEGACY')
    reg_id = (student.registration_id or student.roll_no) if student else None

    return {
        "id": membership.user.id,
        "userId": membership.user.id,
        "rollNumber": reg_id,
        "registerNumber": reg_id,
        "registrationId": reg_id,
        "name": student.full_name if student else membership.user.email,
        "email": membership.user.email,
        "phoneNumber": student.phone_number if student else None,
        "yearOfStudy": student.year_of_study if student else None,
        "department": (
            student.department.name
            if (student and student.department)
            else None
        ),
        "branchCode": getattr(student, 'branch_code', None) if student else None,
        "batchYear": getattr(student, 'batch_year', None) if student else None,
        "graduationYear": getattr(student, 'graduation_year', None) if student else None,
        "bio": student.bio if student else None,
        "membershipRole": membership.membership_role,
        "membershipStatus": membership.membership_status,
        "userStatus": user_status,
        "isLegacy": is_legacy,
        "avatarStyle": getattr(student, 'avatar_style', 'adventurer') if student else 'adventurer',
        "avatarSeed": getattr(student, 'avatar_seed', None) if student else membership.user.email,
        "joinedAt": membership.joined_at.isoformat() if membership.joined_at else None,
        "leftAt": membership.left_at.isoformat() if (hasattr(membership, 'left_at') and membership.left_at) else None
    }

def serialize_event(event):
    return {
        "id": event.id,
        "clubId": event.club_id,
        "name": event.event_name,
        "description": event.event_description,
        "status": event.computed_status.upper() if hasattr(event, 'computed_status') else event.event_status.upper(),
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

    from app.services.notification_service import NotificationService
    for fid in faculty_ids:
        NotificationService.notify_club_created(fid, club.club_name, club.id)

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

def get_club_members(club_id, include_inactive=True):
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

def update_club_member_status(club_id, user_id, active):
    club = Club.query.get_or_404(club_id, description="Club not found")

    membership = ClubMembership.query.filter_by(
        club_id=club_id,
        user_id=user_id
    ).first_or_404(description="Member not found")

    new_status = "ACTIVE" if active else "INACTIVE"

    if membership.membership_status == new_status:
        raise ValueError(
            f"Member is already {new_status.lower()}."
        )

    membership.membership_status = new_status

    if active:
        club.active_members += 1
    else:
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
    Club.query.get_or_404(
        club_id,
        description="Club not found"
    )

    assignment = ClubFaculty.query.filter_by(
        club_id=club_id,
        faculty_id=faculty_id
    ).first()

    if assignment is None:
        raise PermissionError(
            "You are not assigned to this club."
        )

    return assignment

