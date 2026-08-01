EVENT_ID = 1
CLUB_ID = 1


def test_list_events_with_filters(client, admin_headers):
    response = client.get('/api/events', headers=admin_headers)
    assert response.status_code == 200

    events = response.get_json()
    assert isinstance(events, list)
    assert events

    filtered_by_club = client.get('/api/events?clubId=1', headers=admin_headers)
    assert filtered_by_club.status_code == 200
    assert all(item['clubId'] == CLUB_ID for item in filtered_by_club.get_json())

    filtered_by_status = client.get('/api/events?status=live', headers=admin_headers)
    assert filtered_by_status.status_code == 200
    assert all(item['status'] == 'LIVE' for item in filtered_by_status.get_json())

    filtered_by_search = client.get('/api/events?search=hack', headers=admin_headers)
    assert filtered_by_search.status_code == 200
    assert any('Hack' in item['name'] for item in filtered_by_search.get_json())


def test_get_event_detail_and_unauthorized_access(client, admin_headers):
    detail_response = client.get(f'/api/events/{EVENT_ID}', headers=admin_headers)
    assert detail_response.status_code == 200
    assert detail_response.get_json()['id'] == EVENT_ID

    invalid_response = client.get('/api/events/999', headers=admin_headers)
    assert invalid_response.status_code == 404

    unauthenticated_response = client.get(f'/api/events/{EVENT_ID}')
    assert unauthenticated_response.status_code == 401


def test_get_my_events_for_registered_and_participated(client, student_headers, admin_headers):
    register_response = client.post(
        f'/api/events/{EVENT_ID}/register',
        headers=student_headers,
    )
    assert register_response.status_code in {200, 201}

    registered_response = client.get('/api/events/me', headers=student_headers)
    assert registered_response.status_code == 200
    registered_events = registered_response.get_json()
    assert any(item['id'] == EVENT_ID for item in registered_events)

    attendance_response = client.post(
        f'/api/events/{EVENT_ID}/attendance',
        headers=admin_headers,
        json={'userId': 6, 'status': 'PRESENT'},
    )
    assert attendance_response.status_code == 200

    participated_response = client.get('/api/events/me?scope=participated', headers=student_headers)
    assert participated_response.status_code == 200
    participated_events = participated_response.get_json()
    assert any(item['id'] == EVENT_ID for item in participated_events)


def test_create_event_requires_admin_or_faculty(client, student_headers, faculty_headers):
    invalid_response = client.post(
        '/api/events/create',
        headers=student_headers,
        json={
            'clubId': CLUB_ID,
            'name': 'Student Event',
            'startDate': '2026-02-10',
            'endDate': '2026-02-11',
        },
    )
    assert invalid_response.status_code == 403

    valid_response = client.post(
        '/api/events/create',
        headers=faculty_headers,
        json={
            'clubId': CLUB_ID,
            'name': 'Faculty Event',
            'description': 'A faculty-created event',
            'startDate': '2026-02-10',
            'endDate': '2026-02-11',
            'status': 'SCHEDULED',
        },
    )
    assert valid_response.status_code == 201
    created_event = valid_response.get_json()
    assert created_event['name'] == 'Faculty Event'
    assert created_event['clubId'] == CLUB_ID


def test_create_event_validation_errors(client, faculty_headers):
    missing_name_response = client.post(
        '/api/events/create',
        headers=faculty_headers,
        json={
            'clubId': CLUB_ID,
            'startDate': '2026-02-10',
            'endDate': '2026-02-11',
        },
    )
    assert missing_name_response.status_code == 400

    missing_dates_response = client.post(
        '/api/events/create',
        headers=faculty_headers,
        json={
            'clubId': CLUB_ID,
            'name': 'Incomplete Event',
        },
    )
    assert missing_dates_response.status_code == 400


def test_create_event_invalid_club_and_dates(client, faculty_headers):
    invalid_club_response = client.post(
        '/api/events/create',
        headers=faculty_headers,
        json={
            'clubId': 999,
            'name': 'Broken Event',
            'startDate': '2026-02-10',
            'endDate': '2026-02-11',
        },
    )
    assert invalid_club_response.status_code == 404

    invalid_date_response = client.post(
        '/api/events/create',
        headers=faculty_headers,
        json={
            'clubId': CLUB_ID,
            'name': 'Broken Event',
            'startDate': 'not-a-date',
            'endDate': '2026-02-11',
        },
    )
    assert invalid_date_response.status_code == 400


def test_update_event_and_status_permissions(client, student_headers, admin_headers):
    forbidden_update = client.put(
        f'/api/events/{EVENT_ID}/edit',
        headers=student_headers,
        json={'name': 'Blocked Update'},
    )
    assert forbidden_update.status_code == 403

    success_update = client.put(
        f'/api/events/{EVENT_ID}/edit',
        headers=admin_headers,
        json={'name': 'Updated Event Name'},
    )
    assert success_update.status_code == 200
    assert success_update.get_json()['name'] == 'Updated Event Name'

    status_update = client.patch(
        f'/api/events/{EVENT_ID}/status',
        headers=admin_headers,
        json={'status': 'cancelled'},
    )
    assert status_update.status_code == 200
    assert status_update.get_json()['status'] == 'CANCELLED'


def test_update_event_rejects_invalid_dates(client, admin_headers):
    invalid_date_response = client.put(
        f'/api/events/{EVENT_ID}/edit',
        headers=admin_headers,
        json={'startDate': 'bad-date'},
    )
    assert invalid_date_response.status_code == 400


def test_assign_venue_and_invalid_venue(client, admin_headers):
    success_response = client.post(
        f'/api/events/{EVENT_ID}/venue',
        headers=admin_headers,
        json={'venueId': 2},
    )
    assert success_response.status_code == 200
    assert success_response.get_json()['venueId'] == 2

    missing_venue_response = client.post(
        f'/api/events/{EVENT_ID}/venue',
        headers=admin_headers,
        json={'venueId': 999},
    )
    assert missing_venue_response.status_code == 404


def test_assign_venue_requires_venue_id(client, admin_headers):
    response = client.post(
        f'/api/events/{EVENT_ID}/venue',
        headers=admin_headers,
        json={},
    )
    assert response.status_code == 400


def test_register_and_fetch_registrations(client, student_headers, admin_headers):
    register_response = client.post(
        f'/api/events/{EVENT_ID}/register',
        headers=student_headers,
    )
    assert register_response.status_code in {200, 201}

    registrations_response = client.get(
        f'/api/events/{EVENT_ID}/registrations',
        headers=admin_headers,
    )
    assert registrations_response.status_code == 200
    registrations = registrations_response.get_json()
    assert any(item['userId'] == 6 for item in registrations)


def test_manage_schedule_and_announcements(client, admin_headers):
    schedule_response = client.post(
        f'/api/events/{EVENT_ID}/schedule',
        headers=admin_headers,
        json={'time': '09:00', 'activity': 'Opening Session'},
    )
    assert schedule_response.status_code == 200
    assert any(item['activity'] == 'Opening Session' for item in schedule_response.get_json()['schedule'])

    replace_schedule_response = client.put(
        f'/api/events/{EVENT_ID}/schedule',
        headers=admin_headers,
        json=[{'time': '10:00', 'activity': 'Workshop'}],
    )
    assert replace_schedule_response.status_code == 200
    assert replace_schedule_response.get_json()['schedule'][0]['activity'] == 'Workshop'

    announcements_response = client.post(
        f'/api/events/{EVENT_ID}/announcements',
        headers=admin_headers,
        json={'title': 'Notice', 'message': 'Doors open at 8:30'},
    )
    assert announcements_response.status_code == 200
    assert any(item['title'] == 'Notice' for item in announcements_response.get_json()['announcements'])

    replace_announcement_response = client.put(
        f'/api/events/{EVENT_ID}/announcements',
        headers=admin_headers,
        json=[{'title': 'Reminder', 'message': 'Bring your ID card'}],
    )
    assert replace_announcement_response.status_code == 200
    assert replace_announcement_response.get_json()['announcements'][0]['title'] == 'Reminder'


def test_manage_schedule_and_announcements_validation_errors(client, admin_headers):
    missing_activity_response = client.post(
        f'/api/events/{EVENT_ID}/schedule',
        headers=admin_headers,
        json={'time': '09:00'},
    )
    assert missing_activity_response.status_code == 400

    missing_message_response = client.post(
        f'/api/events/{EVENT_ID}/announcements',
        headers=admin_headers,
        json={'title': 'Notice'},
    )
    assert missing_message_response.status_code == 400


def test_manage_attendance_prizes_and_organizers(client, admin_headers):
    attendance_response = client.put(
        f'/api/events/{EVENT_ID}/attendance',
        headers=admin_headers,
        json=[{'userId': 6, 'status': 'ABSENT'}],
    )
    assert attendance_response.status_code == 200
    assert any(item['userId'] == 6 for item in attendance_response.get_json()['attendance'])

    get_attendance_response = client.get(f'/api/events/{EVENT_ID}/attendance', headers=admin_headers)
    assert get_attendance_response.status_code == 200
    assert isinstance(get_attendance_response.get_json(), list)

    prizes_response = client.post(
        f'/api/events/{EVENT_ID}/prizes',
        headers=admin_headers,
        json={'title': 'Best Innovation', 'winnerName': 'Rahul'},
    )
    assert prizes_response.status_code == 200
    assert any(item['title'] == 'Best Innovation' for item in prizes_response.get_json()['prizes'])

    organizers_response = client.post(
        f'/api/events/{EVENT_ID}/organizers',
        headers=admin_headers,
        json={'userId': 6, 'role': 'LEAD'},
    )
    assert organizers_response.status_code == 200
    assert any(item['userId'] == 6 for item in organizers_response.get_json()['organizers'])


def test_manage_prizes_and_organizers_listing(client, admin_headers):
    prizes_list_response = client.get(f'/api/events/{EVENT_ID}/prizes', headers=admin_headers)
    assert prizes_list_response.status_code == 200
    assert isinstance(prizes_list_response.get_json(), list)

    organizers_list_response = client.get(f'/api/events/{EVENT_ID}/organizers', headers=admin_headers)
    assert organizers_list_response.status_code == 200
    assert isinstance(organizers_list_response.get_json(), list)


def test_manage_volunteers_and_update_state(client, student_headers, admin_headers):
    volunteer_response = client.post(
        f'/api/events/{EVENT_ID}/volunteers',
        headers=student_headers,
        json={},
    )
    assert volunteer_response.status_code == 200
    volunteers = volunteer_response.get_json()['volunteers']
    assert any(item['userId'] == 6 for item in volunteers)

    volunteers_list_response = client.get(f'/api/events/{EVENT_ID}/volunteers', headers=student_headers)
    assert volunteers_list_response.status_code == 200
    assert isinstance(volunteers_list_response.get_json(), list)

    volunteer_id = next(item['id'] for item in volunteers if item['userId'] == 6)
    update_volunteer_response = client.patch(
        f'/api/events/{EVENT_ID}/volunteers/{volunteer_id}',
        headers=admin_headers,
        json={'status': 'APPROVED'},
    )
    assert update_volunteer_response.status_code == 200
    assert update_volunteer_response.get_json()['status'] == 'APPROVED'


def test_venues_listing_and_crud(client, admin_headers, student_headers):
    list_response = client.get('/api/venues', headers=admin_headers)
    assert list_response.status_code == 200
    assert isinstance(list_response.get_json(), list)

    detail_response = client.get('/api/venues/1', headers=admin_headers)
    assert detail_response.status_code == 200
    assert detail_response.get_json()['id'] == 1

    forbidden_create_response = client.post(
        '/api/venues/create',
        headers=student_headers,
        json={'name': 'Restricted Venue', 'location': 'Block 7', 'capacity': 80},
    )
    assert forbidden_create_response.status_code == 403

    created_response = client.post(
        '/api/venues/create',
        headers=admin_headers,
        json={'name': 'Test Arena', 'location': 'Block 7', 'type': 'LAB', 'capacity': 80},
    )
    assert created_response.status_code == 201
    assert created_response.get_json()['name'] == 'Test Arena'

    update_response = client.put(
        f"/api/venues/{created_response.get_json()['id']}/edit",
        headers=admin_headers,
        json={'name': 'Updated Arena', 'capacity': 100},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()['name'] == 'Updated Arena'

    status_response = client.patch(
        f"/api/venues/{created_response.get_json()['id']}/status",
        headers=admin_headers,
        json={'status': 'MAINTENANCE'},
    )
    assert status_response.status_code == 200
    assert status_response.get_json()['availabilityStatus'] == 'MAINTENANCE'


def test_venues_search_and_validation(client, admin_headers):
    search_response = client.get('/api/venues?search=lab', headers=admin_headers)
    assert search_response.status_code == 200
    assert isinstance(search_response.get_json(), list)

    duplicate_response = client.post(
        '/api/venues/create',
        headers=admin_headers,
        json={'name': 'Innovation Lab', 'location': 'Block 1', 'capacity': 60},
    )
    assert duplicate_response.status_code == 409

    missing_status_response = client.patch(
        '/api/venues/1/status',
        headers=admin_headers,
        json={},
    )
    assert missing_status_response.status_code == 400
