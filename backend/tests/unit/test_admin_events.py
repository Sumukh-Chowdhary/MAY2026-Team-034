EVENT_ID = 1
INVALID_EVENT = 999

AI_CLUB = 1

INNOVATION_LAB = 1
MAIN_AUDITORIUM = 2

RAHUL_USER_ID = 24
ANANYA_USER_ID = 25

# Event Details

def test_get_event(client, admin_headers):
    response = client.get(
        f"/api/events/{EVENT_ID}",
        headers=admin_headers
    )

    assert response.status_code == 200

    event = response.get_json()


    assert event["id"] == EVENT_ID
    assert "AI" in event["name"] and "Hack" in event["name"]

    assert event["clubName"] == "AI Club"
    assert event["venueName"] == "Innovation Lab"




def test_get_invalid_event(client, admin_headers):
    response = client.get(
        f"/api/events/{INVALID_EVENT}",
        headers=admin_headers
    )

    assert response.status_code == 404




# Venue

def test_assign_venue(client, admin_headers):
    response = client.post(
        f"/api/events/{EVENT_ID}/venue",
        headers=admin_headers,
        json={
            "venueId": MAIN_AUDITORIUM
        }
    )

    assert response.status_code == 200

    event = response.get_json()

    assert event["id"] == EVENT_ID
    assert event["venueId"] == MAIN_AUDITORIUM




# Schedule

def test_add_schedule(client, admin_headers):
    response = client.post(
        f"/api/events/{EVENT_ID}/schedule",
        headers=admin_headers,
        json={
            "time": "11:00",
            "activity": "Project Demonstration"
        }
    )

    assert response.status_code == 200

    event = response.get_json()

    assert any(
        item["activity"] == "Project Demonstration"
        for item in event["schedule"]
    )




def test_replace_schedule(client, admin_headers):
    response = client.put(
        f"/api/events/{EVENT_ID}/schedule",
        headers=admin_headers,
        json=[
            {
                "time": "09:00",
                "activity": "Opening Ceremony"
            },
            {
                "time": "10:00",
                "activity": "Coding Round"
            }
        ]
    )

    assert response.status_code == 200

    event = response.get_json()

    assert len(event["schedule"]) == 2

    assert event["schedule"][0]["activity"] == "Opening Ceremony"
    assert event["schedule"][1]["activity"] == "Coding Round"





# Announcements

def test_add_announcement(client, admin_headers):
    response = client.post(
        f"/api/events/{EVENT_ID}/announcements",
        headers=admin_headers,
        json={
            "title": "Important Update",
            "message": "Reporting time changed to 9 AM."
        }
    )

    assert response.status_code == 200

    event = response.get_json()

    assert any(
        item["title"] == "Important Update"
        for item in event["announcements"]
    )


def test_replace_announcements(client, admin_headers):
    response = client.put(
        f"/api/events/{EVENT_ID}/announcements",
        headers=admin_headers,
        json=[
            {
                "title": "Notice",
                "message": "Registration closes today."
            },
            {
                "title": "Reminder",
                "message": "Bring your ID card."
            }
        ]
    )

    assert response.status_code == 200

    event = response.get_json()

    assert len(event["announcements"]) == 2

    assert event["announcements"][0]["title"] == "Notice"
    assert event["announcements"][1]["title"] == "Reminder"




# Attendance

def test_get_attendance(client, admin_headers):
    response = client.get(
        f"/api/events/{EVENT_ID}/attendance",
        headers=admin_headers
    )

    assert response.status_code == 200

    attendance = response.get_json()

    assert isinstance(attendance, (list, dict))




def test_replace_attendance(client, admin_headers):
    response = client.put(
        f"/api/events/{EVENT_ID}/attendance",
        headers=admin_headers,
        json=[
            {
                "userId": RAHUL_USER_ID,
                "status": "PRESENT"
            }
        ]
    )

    assert response.status_code == 200

    event = response.get_json()

    assert any(
        item["userId"] == RAHUL_USER_ID
        for item in event["attendance"]
    )




# Authorization

def test_student_cannot_assign_venue(client, app, student_headers):
    with app.app_context():
        from app.models.events import Event
        from app.models.user import User
        from app.routes.events import _can_manage_event
        user_24 = User.query.get(24)
        unauth_event = next((ev for ev in Event.query.all() if not _can_manage_event(ev, user_24)), None)
        target_id = unauth_event.id if unauth_event else 10

    response = client.post(
        f"/api/events/{target_id}/venue",
        headers=student_headers,
        json={
            "venueId": 1
        }
    )

    assert response.status_code == 403



def test_student_cannot_manage_schedule(client, app, student_headers):
    with app.app_context():
        from app.models.events import Event
        from app.models.user import User
        from app.routes.events import _can_manage_event
        user_24 = User.query.get(24)
        unauth_event = next((ev for ev in Event.query.all() if not _can_manage_event(ev, user_24)), None)
        target_id = unauth_event.id if unauth_event else 10

    response = client.post(
        f"/api/events/{target_id}/schedule",
        headers=student_headers,
        json={
            "time": "09:00",
            "activity": "Opening Session"
        }
    )

    assert response.status_code == 403



def test_unauthenticated_get_event(client):
    response = client.get(
        f"/api/events/{EVENT_ID}"
    )

    assert response.status_code == 401