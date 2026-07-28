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