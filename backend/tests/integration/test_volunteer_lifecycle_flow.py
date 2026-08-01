import pytest

def test_volunteer_lifecycle_integration(client, student_headers, admin_headers):
    event_id = 1 # AI Hack Sprint
    
    # 1. Student registers as a volunteer for the event
    register_resp = client.post(
        f"/api/events/{event_id}/volunteers",
        headers=student_headers,
        json={}
    )
    assert register_resp.status_code == 200
    volunteers = register_resp.get_json()["volunteers"]
    
    # User ID 6 is Rahul (logged in via student_headers)
    student_vol = next(item for item in volunteers if item["userId"] == 6)
    assert student_vol["status"] == "PENDING"
    volunteer_entry_id = student_vol["id"]
    
    # 2. Verify that a normal student cannot approve their own volunteer status
    forbidden_resp = client.patch(
        f"/api/events/{event_id}/volunteers/{volunteer_entry_id}",
        headers=student_headers,
        json={"status": "APPROVED"}
    )
    assert forbidden_resp.status_code == 403
    
    # 3. Admin approves the volunteer request
    approve_resp = client.patch(
        f"/api/events/{event_id}/volunteers/{volunteer_entry_id}",
        headers=admin_headers,
        json={"status": "APPROVED"}
    )
    assert approve_resp.status_code == 200
    assert approve_resp.get_json()["status"] == "APPROVED"
    
    # 4. Verify that the update is persisted in the volunteers listing
    list_resp = client.get(
        f"/api/events/{event_id}/volunteers",
        headers=student_headers
    )
    assert list_resp.status_code == 200
    updated_volunteers = list_resp.get_json()
    
    target_vol = next(item for item in updated_volunteers if item["id"] == volunteer_entry_id)
    assert target_vol["status"] == "APPROVED"
