import pytest

def test_module_21_student_organizer_full_flow(client, student_headers):
    # 1. Student Rahul (User ID 6) fetches events for AI Club (Club ID 1)
    res_events = client.get("/api/events?clubId=1", headers=student_headers)
    assert res_events.status_code == 200

    # 2. Student updates event schedule for Event ID 1 (AI Hack Sprint)
    res_schedule = client.post(
        "/api/events/1/schedule",
        headers=student_headers,
        json={"time": "09:30", "activity": "Keynote & Problem Statements Unveiling"}
    )
    assert res_schedule.status_code == 200

    # 3. Student posts an event announcement
    res_announcement = client.post(
        "/api/events/1/announcements",
        headers=student_headers,
        json={"title": "Venue Update", "message": "Hackathon shifted to Lab 3."}
    )
    assert res_announcement.status_code == 200

    # 4. Student updates event prizes/winners
    res_prizes = client.post(
        "/api/events/1/prizes",
        headers=student_headers,
        json={"title": "1st Prize", "winnerName": "Rahul Sharma", "description": "Best overall project"}
    )
    assert res_prizes.status_code == 200

    # 5. Student raises Venue Request Ticket
    res_venue_req = client.post(
        "/api/requests",
        headers=student_headers,
        json={
            "requestType": "VENUE_REQUEST",
            "title": "Venue Request: Main Auditorium for AI Sprint",
            "description": "Need Main Auditorium from 9 AM to 5 PM",
            "priority": "HIGH",
            "referenceType": "EVENT",
            "referenceId": 1,
            "referenceName": "AI Hack Sprint"
        }
    )
    assert res_venue_req.status_code == 201