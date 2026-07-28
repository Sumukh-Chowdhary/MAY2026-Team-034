from flask import Blueprint, request, jsonify
from app.models import db, User, Role, Department, FacultyProfile
from app.models.club import Club,ClubFaculty,ClubOrganizer,ClubMembership
from app.utils.auth_jwt import jwt_required, roles_required
from sqlalchemy import case

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@jwt_required
@roles_required('ADMIN')
@admin_bp.get('/clubs')
def get_clubs():
    clubs = Club.query.order_by(
        case(
            (Club.club_status == 'ACTIVE',0),
            else_=1
        ),
        Club.club_name.asc()
    ).all()
    response = []
    for club in clubs:
        organizers = [
            {
                "id":organizer.user.id,
                "name":organizer.user.student_profile.full_name
                if organizer.user.student_profile
                else organizer.user.faculty_profile.full_name
            }
            for organizer in club.organizers
        ]

        faculty = [
            {
                "id":advisor.faculty.id,
                "name":advisor.faculty.faculty_profile.full_name
            }
            for advisor in club.faculty_coordinators
        ]

        response.append({
            "id": club.id,
            "name": club.club_name,
            "category": club.club_category,
            "description": club.club_description,
            "logo": club.club_logo,
            "status": club.club_status,
            "totalMembers": club.total_members,
            "activeMembers": club.active_members,
            "organizers": organizers,
            "faculty": faculty,
            "createdAt": club.created_at.isoformat()
        })
    return jsonify(response),200

@jwt_required
@roles_required("ADMIN")
@admin_bp.route("/clubs/<int:club_id>/status", methods=["PATCH"])
def update_club_status(club_id):
    club = Club.query.get_or_404(club_id)
    data = request.get_json() or {}
    status = data.get("status")
    if status not in ["ACTIVE", "INACTIVE"]:
        return jsonify({
            "error":"Invalid status"
        }),400

    club.club_status = status
    db.session.commit()
    return jsonify(club.to_dict()),200

@jwt_required
@roles_required("ADMIN")
@admin_bp.get("/clubs/faculty-details")
def get_faculty_details():
    faculty = (
        FacultyProfile.query
        .order_by(FacultyProfile.full_name)
        .all()
    )

    response = []

    for member in faculty:
        response.append({
            "id": member.user_id,
            "name": member.full_name,
            "designation": member.designation,
            "department": (
                member.department.name
                if member.department
                else None
            )
        })

    return jsonify(response), 200

@jwt_required
@roles_required("ADMIN")
@admin_bp.post("/clubs/create")
def create_club():
    data = request.get_json() or {}

    name = (data.get("name") or "").strip()
    category = (data.get("category") or "").strip()
    description = (data.get("description") or "").strip()
    logo = data.get("logo")
    faculty_ids = data.get("facultyCoordinatorIds", [])

    if not name:
        return jsonify({"error": "Club name is required."}), 400

    if not category:
        return jsonify({"error": "Category is required."}), 400

    if not description:
        return jsonify({"error": "Description is required."}), 400

    if not faculty_ids:
        return jsonify({"error": "Select at least one faculty coordinator."}), 400

    if Club.query.filter_by(club_name=name).first():
        return jsonify({"error": "A club with this name already exists."}), 409

    VALID_CATEGORIES = {
        "Technology",
        "Academic",
        "Sports",
        "Arts",
        "Cultural",
        "Entrepreneurship",
        "Social Service",
        "General"
    }

    if category not in VALID_CATEGORIES:
        return jsonify({
            "error":"Invalid category."
        }),400

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
        return jsonify({
            "error": "Invalid faculty coordinator(s).",
            "invalidFacultyIds": invalid_ids
        }), 400

    try:
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
        return jsonify(club.to_dict()), 201

    except Exception as error:
        db.session.rollback()
        return jsonify({
            "error": "Failed to create club.",
            "details": str(error)
        }), 500

@jwt_required
@roles_required("ADMIN")
@admin_bp.put("/clubs/<int:club_id>/edit")
def update_club(club_id):

    data = request.get_json() or {}

    name = (data.get("name") or "").strip()
    category = (data.get("category") or "").strip()
    description = (data.get("description") or "").strip()
    logo = data.get("logo")
    faculty_ids = data.get("facultyCoordinatorIds", [])

    if not name:
        return jsonify({"error": "Club name is required."}), 400

    if not category:
        return jsonify({"error": "Category is required."}), 400

    if not description:
        return jsonify({"error": "Description is required."}), 400

    if not faculty_ids:
        return jsonify({"error": "Select at least one faculty coordinator."}), 400

    club = Club.query.get_or_404(club_id)

    existing = Club.query.filter(
        db.func.lower(Club.club_name) == name.lower(),
        Club.id != club_id
    ).first()

    if existing:
        return jsonify({
            "error": "Another club already uses this name."
        }), 409

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
        return jsonify({
            "error": "Invalid faculty coordinator(s).",
            "invalidFacultyIds": invalid_ids
        }), 400

    try:
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
        return jsonify(club.to_dict()), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({
            "error": "Failed to update club.",
            "details": str(error)
        }), 500