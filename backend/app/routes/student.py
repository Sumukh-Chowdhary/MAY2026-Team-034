from datetime import datetime

from flask import Blueprint, request, jsonify, g # type: ignore

from app.models import db, User
from app.models.club import Club, ClubFaculty, ClubOrganizer, ClubMembership

from app.utils.auth_jwt import jwt_required, roles_required


student_bp = Blueprint(
    "student",
    __name__,
    url_prefix="/api/student"
)

@student_bp.get("/my-clubs")
@jwt_required
@roles_required("STUDENT")
def get_my_clubs():

    memberships = ClubMembership.query.filter_by(
        user_id=g.current_user.id,
        membership_status="ACTIVE"
    ).all()

    response = []

    for membership in memberships:

        club = membership.club

        organizers = [
            {
                "id": organizer.user.id,
                "name": (
                    organizer.user.student_profile.full_name
                    if organizer.user.student_profile
                    else organizer.user.faculty_profile.full_name
                )
            }
            for organizer in club.organizers
        ]

        faculty = [
            {
                "id": advisor.faculty.id,
                "name": advisor.faculty.faculty_profile.full_name
            }
            for advisor in club.faculty_coordinators
        ]

        response.append({
            "id": club.id,
            "name": club.club_name,
            "description": club.club_description,
            "category": club.club_category,
            "logo": club.club_logo,
            "status": club.club_status,
            "totalMembers": club.total_members,
            "activeMembers": club.active_members,
            "membershipRole": membership.membership_role,
            "organizers": organizers,
            "faculty": faculty,
        })

    return jsonify(response), 200

@student_bp.get("/clubs")
@jwt_required
@roles_required("STUDENT")
def get_clubs():
    clubs = Club.query.order_by(Club.club_name).all()

    response = []

    for club in clubs:

        organizers = [
            {
                "id": organizer.user.id,
                "name":
                    organizer.user.student_profile.full_name
                    if organizer.user.student_profile
                    else organizer.user.faculty_profile.full_name
            }
            for organizer in club.organizers
        ]

        faculty = [
            {
                "id": advisor.faculty.id,
                "name": advisor.faculty.faculty_profile.full_name
            }
            for advisor in club.faculty_coordinators
        ]

        response.append({
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
        })

    return jsonify(response), 200

@student_bp.route("/clubs/<int:club_id>/join", methods=["POST"])
@jwt_required
@roles_required("STUDENT")
def join_club(club_id):
    current_user = g.current_user

    # Check if club exists
    club = Club.query.get(club_id)
    if not club:
        return jsonify({"error": "Club not found"}), 404

    # Check if club is active
    if club.club_status != "ACTIVE":
        return jsonify({"error": "Cannot join an archived or inactive club"}), 400

    # Check for an existing membership
    membership = ClubMembership.query.filter_by(
        club_id=club.id,
        user_id=current_user.id
    ).first()

    if membership:

        # Already an active member
        if membership.membership_status == "ACTIVE":
            return jsonify({"message": "You are already a member of this club"}), 409

        # Reactivate previous membership
        membership.membership_status = "ACTIVE"
        membership.joined_at = datetime.utcnow()

        club.active_members += 1

    else:
        # Create a new membership
        membership = ClubMembership(
            club_id=club.id,
            user_id=current_user.id,
            membership_role="MEMBER",
            membership_status="ACTIVE"
        )

        db.session.add(membership)

        club.total_members += 1
        club.active_members += 1

    db.session.commit()

    return jsonify({
        "message": "Joined club successfully",
        "membershipStatus": membership.membership_status,
        "activeMembers": club.active_members,
        "totalMembers": club.total_members
    }), 200

@student_bp.route("/clubs/<int:club_id>/leave", methods=["POST"])
@jwt_required
@roles_required("STUDENT")
def leave_club(club_id):
    current_user = g.current_user

    # Check if club exists
    club = Club.query.get(club_id)
    if not club:
        return jsonify({"error": "Club not found"}), 404

    # Find membership
    membership = ClubMembership.query.filter_by(
        club_id=club.id,
        user_id=current_user.id
    ).first()

    if not membership:
        return jsonify({"message": "You are not a member of this club"}), 404

    if membership.membership_status != "ACTIVE":
        return jsonify({"message": "Membership is already inactive"}), 409

    # Deactivate membership
    membership.membership_status = "INACTIVE"

    # Update club counts
    club.active_members -= 1

    db.session.commit()

    return jsonify({
        "message": "Left club successfully",
        "clubId": club.id,
        "membershipStatus": membership.membership_status,
        "activeMembers": club.active_members,
        "totalMembers": club.total_members
    }), 200