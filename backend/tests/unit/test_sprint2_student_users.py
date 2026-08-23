# Sprint 2 – Student & User API tests
# Covers endpoints that had NO tests in Sprint 1:
#   PUT /api/student/clubs/<id>/details
#   GET /api/users            (no auth required)
#   GET /api/users/<id>
#   PUT /api/users/<id>
#   DELETE /api/users/<id>    (admin only)

AI_CLUB      = 1
INVALID_CLUB = 999
RAHUL_ID     = 24   # first student in seed (2 admins=1..2, 21 faculty/principal=3..23)
ANANYA_ID    = 25
ADMIN_ID     = 1


# ===========================================================================
# PUT /api/student/clubs/<id>/details   (organizer-only club edit)
# ===========================================================================

def test_organizer_can_update_club_details(client, student_headers):
    """Rahul is seeded as club organizer for AI Club — should succeed."""
    response = client.put(
        f'/api/student/clubs/{AI_CLUB}/details',
        headers=student_headers,
        json={
            'description': 'Updated description by organizer',
            'logo': 'star',
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body['description'] == 'Updated description by organizer'


def test_organizer_update_only_description(client, student_headers):
    """Partial update with only description field."""
    response = client.put(
        f'/api/student/clubs/{AI_CLUB}/details',
        headers=student_headers,
        json={'description': 'Only description changed'},
    )
    assert response.status_code == 200
    assert response.get_json()['description'] == 'Only description changed'


def test_organizer_update_only_logo(client, student_headers):
    """Partial update with only logo field."""
    response = client.put(
        f'/api/student/clubs/{AI_CLUB}/details',
        headers=student_headers,
        json={'logo': 'rocket'},
    )
    assert response.status_code == 200



def test_non_organizer_student_blocked(client):
    """Ananya is NOT organizer of AI Club — must get 403."""
    login = client.post(
        '/api/auth/login',
        json={'username': 'Y25CS002', 'password': 'student123'},
    )
    assert login.status_code == 200
    token = login.get_json()['token']
    headers = {'Authorization': f'Bearer {token}'}

    response = client.put(
        f'/api/student/clubs/{AI_CLUB}/details',
        headers=headers,
        json={'description': 'Should be blocked'},
    )
    assert response.status_code == 403


def test_update_club_details_invalid_club(client, student_headers):
    """Non-existent club returns 404."""
    response = client.put(
        f'/api/student/clubs/{INVALID_CLUB}/details',
        headers=student_headers,
        json={'description': 'Ghost club'},
    )
    assert response.status_code in {403, 404}


def test_update_club_details_unauthenticated(client):
    """Unauthenticated request returns 401."""
    response = client.put(
        f'/api/student/clubs/{AI_CLUB}/details',
        json={'description': 'No auth'},
    )
    assert response.status_code == 401


def test_faculty_cannot_update_student_club_details(client, faculty_headers):
    """Faculty must get 403 (route is STUDENT-only)."""
    response = client.put(
        f'/api/student/clubs/{AI_CLUB}/details',
        headers=faculty_headers,
        json={'description': 'Faculty blocked'},
    )
    assert response.status_code == 403


# ===========================================================================
# GET /api/users  (no auth required)
# ===========================================================================

def test_get_users_returns_list(client):
    """Public endpoint returns a list of all users."""
    response = client.get('/api/users')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_users_not_empty(client):
    """Seeded database must have at least one user."""
    response = client.get('/api/users')
    assert response.status_code == 200
    assert len(response.get_json()) > 0


def test_get_users_filter_by_role_student(client):
    """Filtering by STUDENT role returns only students."""
    response = client.get('/api/users?role=STUDENT')
    assert response.status_code == 200
    users = response.get_json()
    assert all(u['role'] == 'STUDENT' for u in users)


def test_get_users_filter_by_role_faculty(client):
    """Filtering by FACULTY role returns only faculty."""
    response = client.get('/api/users?role=FACULTY')
    assert response.status_code == 200
    users = response.get_json()
    assert all(u['role'] == 'FACULTY' for u in users)


def test_get_users_search_by_name(client):
    """Search for 'Rahul' must return at least one result."""
    response = client.get('/api/users?search=Rahul')
    assert response.status_code == 200
    users = response.get_json()
    assert len(users) >= 1
    assert any('Rahul' in u['name'] for u in users)


def test_get_users_search_no_match(client):
    """Search with no matching name returns empty list."""
    response = client.get('/api/users?search=ZZZNOMATCHZZZ')
    assert response.status_code == 200
    assert response.get_json() == []


# ===========================================================================
# GET /api/users/<id>
# ===========================================================================

def test_get_user_by_id(client):
    """Fetching a seeded user by ID returns correct data."""
    response = client.get(f'/api/users/{RAHUL_ID}')
    assert response.status_code == 200
    user = response.get_json()
    assert user['id'] == RAHUL_ID


def test_get_user_invalid_id(client):
    """Non-existent user ID returns 404."""
    response = client.get('/api/users/9999')
    assert response.status_code == 404


def test_get_user_has_expected_fields(client):
    """User response contains id, name, email, role."""
    response = client.get(f'/api/users/{RAHUL_ID}')
    assert response.status_code == 200
    user = response.get_json()
    for field in ('id', 'name', 'email', 'role'):
        assert field in user, f"Missing field: {field}"


# ===========================================================================
# PUT /api/users/<id>  (update own profile or admin updates any)
# ===========================================================================

def test_user_can_update_own_profile(client, student_headers):
    """Student can update their own profile bio."""
    response = client.put(
        f'/api/users/{RAHUL_ID}',
        headers=student_headers,
        json={'bio': 'Updated bio by Rahul'},
    )
    assert response.status_code == 200


def test_user_cannot_update_other_profile(client, student_headers):
    """Student cannot update another user's profile — 403."""
    response = client.put(
        f'/api/users/{ANANYA_ID}',  # Ananya's ID
        headers=student_headers,
        json={'bio': 'Should be rejected'},
    )
    assert response.status_code == 403


def test_admin_can_update_any_profile(client, admin_headers):
    """Admin can update any user's profile."""
    response = client.put(
        f'/api/users/{RAHUL_ID}',
        headers=admin_headers,
        json={'bio': 'Admin updated Rahul bio'},
    )
    assert response.status_code == 200


def test_admin_can_update_account_status(client, admin_headers):
    """Admin can change account status via the users endpoint."""
    response = client.put(
        f'/api/users/{RAHUL_ID}',
        headers=admin_headers,
        json={'accountStatus': 'SUSPENDED'},
    )
    assert response.status_code == 200
    assert response.get_json()['status'] == 'SUSPENDED'


def test_update_user_unauthenticated(client):
    """Unauthenticated profile update returns 401."""
    response = client.put(
        f'/api/users/{RAHUL_ID}',
        json={'bio': 'no auth'},
    )
    assert response.status_code == 401


def test_update_user_invalid_id(client, admin_headers):
    """Admin trying to update non-existent user returns 404."""
    response = client.put(
        '/api/users/9999',
        headers=admin_headers,
        json={'bio': 'ghost user'},
    )
    assert response.status_code == 404


# ===========================================================================
# DELETE /api/users/<id>  (admin only)
# ===========================================================================

def test_admin_can_delete_user(client, admin_headers):
    """Admin can delete a user."""
    # Delete Ananya — she won't affect other tests since each test gets fresh DB
    response = client.delete(f'/api/users/{ANANYA_ID}', headers=admin_headers)
    assert response.status_code == 200
    body = response.get_json()
    assert 'message' in body


def test_student_cannot_delete_user(client, student_headers):
    """Student must get 403 when trying to delete."""
    response = client.delete(f'/api/users/{ANANYA_ID}', headers=student_headers)
    assert response.status_code == 403


def test_faculty_cannot_delete_user(client, faculty_headers):
    """Faculty must get 403 when trying to delete."""
    response = client.delete(f'/api/users/{ANANYA_ID}', headers=faculty_headers)
    assert response.status_code == 403


def test_delete_nonexistent_user(client, admin_headers):
    """Deleting a non-existent user returns 404."""
    response = client.delete('/api/users/9999', headers=admin_headers)
    assert response.status_code == 404


def test_delete_user_unauthenticated(client):
    """Unauthenticated delete returns 401."""
    response = client.delete(f'/api/users/{ANANYA_ID}')
    assert response.status_code == 401


def test_deleted_user_not_found(client, admin_headers):
    """After deletion, the user must no longer be found by GET."""
    del_resp = client.delete(f'/api/users/{ANANYA_ID}', headers=admin_headers)
    assert del_resp.status_code == 200

    get_resp = client.get(f'/api/users/{ANANYA_ID}')
    assert get_resp.status_code == 404
