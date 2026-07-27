from flask import Blueprint, request, jsonify
from app.models import db, User, Role, Department
from app.models.club import Club,ClubFaculty,ClubOrganizer,ClubMembership
from app.utils.auth_jwt import jwt_required, roles_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@jwt_required
@roles_required('ADMIN')
@admin_bp.get('/clubs')
def get_clubs():
    clubs = Club.query.order_by(Club.club_name).all()
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