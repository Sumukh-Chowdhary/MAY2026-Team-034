import pytest
from app.models.tickets import Request, RequestApproval, ApprovalStatus

def test_create_request_unauthorized(client):
    """Test that unauthorized users cannot create requests."""
    response = client.post("/api/requests", json={
        "requestType": "CLUB_BUDGET",
        "title": "Need funds",
        "description": "For an event"
    })
    assert response.status_code == 401

def test_create_request_default_workflow(client, student_headers, app):
    """Test creating a request as a student using default workflow."""
    response = client.post("/api/requests", headers=student_headers, json={
        "requestType": "BUDGET_REQUEST",
        "title": "Need funds",
        "description": "For an event",
        "referenceType": "CLUB",
        "referenceName": "Tech Club",
        "referenceId": 1
    })
    assert response.status_code == 201, response.get_json()
    data = response.get_json()["data"]
    
    assert data["title"] == "Need funds"
    assert data["requestType"] == "BUDGET_REQUEST"
    assert data["workflowStatus"] == "PENDING"
    # Budget request needs faculty + hod + principal according to rules (if configured)
    # Default is just to verify it created.
    assert len(data["approvals"]) > 0

def test_create_request_custom_approvers(client, student_headers, app):
    """Test creating a request with a custom approval chain."""
    response = client.post("/api/requests", headers=student_headers, json={
        "requestType": "BUDGET_REQUEST",
        "title": "Custom request",
        "description": "Custom workflow",
        "referenceType": "CLUB",
        "referenceId": 1,
        "approvers": [
            {"approverId": 3, "role": "HOD"},
            {"approverId": 2, "role": "PRINCIPAL"}
        ]
    })
    assert response.status_code == 201, response.get_json()
    data = response.get_json()["data"]
    
    with app.app_context():
        assert len(data["approvals"]) == 2
        assert data["approvals"][0]["approverId"] == 3
        assert data["approvals"][1]["approverId"] == 2

def test_get_requests(client, student_headers):
    """Test fetching user's own requests."""
    # Create one first
    res = client.post("/api/requests", headers=student_headers, json={
        "requestType": "BUDGET_REQUEST",
        "title": "Get My Requests Test",
        "description": "Test",
        "referenceType": "CLUB",
        "referenceId": 1
    })
    assert res.status_code == 201, res.get_json()
    
    response = client.get("/api/requests", headers=student_headers)
    assert response.status_code == 200, response.get_json()
    data = response.get_json()["data"]
    assert len(data) >= 1
    assert any(r["title"] == "Get My Requests Test" for r in data)

def test_approve_request(client, student_headers, faculty_headers):
    """Test the approval of a step in a request."""
    # 1. Student creates request with faculty as custom approver
    res = client.post("/api/requests", headers=student_headers, json={
        "requestType": "BUDGET_REQUEST",
        "title": "Approval Test",
        "description": "Testing approval flow",
        "referenceType": "CLUB",
        "referenceId": 1,
        "approvers": [
            {"approverId": 4, "role": "FACULTY"} # User 4 is Dr. Meena Rao
        ]
    })
    assert res.status_code == 201, res.get_json()
    req_id = res.get_json()["data"]["id"]
    
    # 2. Student tries to approve it (Should fail/unauthorized)
    res_fail = client.post(f"/api/requests/{req_id}/approve", headers=student_headers)
    assert res_fail.status_code in [403, 404] 
    
    # 3. Faculty approves it
    res_success = client.post(f"/api/requests/{req_id}/approve", headers=faculty_headers, json={"remarks": "Looks good"})
    assert res_success.status_code == 200
    assert res_success.get_json()["data"]["workflowStatus"] == "APPROVED" # Since it was the only approver

def test_reject_request(client, student_headers, faculty_headers):
    """Test rejecting a request."""
    res = client.post("/api/requests", headers=student_headers, json={
        "requestType": "BUDGET_REQUEST",
        "title": "Reject Test",
        "description": "Testing reject flow",
        "referenceType": "CLUB",
        "referenceId": 1,
        "approvers": [{"approverId": 4, "role": "FACULTY"}]
    })
    assert res.status_code == 201, res.get_json()
    req_id = res.get_json()["data"]["id"]
    
    # Faculty rejects it
    res_reject = client.post(f"/api/requests/{req_id}/reject", headers=faculty_headers, json={"remarks": "Not feasible"})
    assert res_reject.status_code == 200
    assert res_reject.get_json()["data"]["workflowStatus"] == "REJECTED"

def test_request_changes_and_resubmit(client, student_headers, faculty_headers):
    """Test asking for changes and student resubmitting."""
    res = client.post("/api/requests", headers=student_headers, json={
        "requestType": "BUDGET_REQUEST",
        "title": "Change Request Test",
        "description": "Initial description",
        "referenceType": "CLUB",
        "referenceId": 1,
        "approvers": [{"approverId": 4, "role": "FACULTY"}]
    })
    assert res.status_code == 201, res.get_json()
    req_id = res.get_json()["data"]["id"]
    
    # Faculty requests changes
    res_faculty = client.post(f"/api/requests/{req_id}/request-changes", headers=faculty_headers, json={"remarks": "Need more info"})
    assert res_faculty.status_code == 200
    
    res_verify = client.get(f"/api/requests/{req_id}", headers=student_headers)
    assert res_verify.get_json()["data"]["workflowStatus"] == "CHANGES_REQUESTED"
    
    # Student resubmits
    res_resubmit = client.post(f"/api/requests/{req_id}/resubmit", headers=student_headers, json={
        "title": "Change Request Test",
        "description": "Updated description with more info",
        "approvers": [{"approverId": 4, "role": "FACULTY"}]
    })
    assert res_resubmit.status_code == 200
    
    res_verify2 = client.get(f"/api/requests/{req_id}", headers=student_headers)
    data = res_verify2.get_json()["data"]
    assert data["workflowStatus"] == "PENDING"
    assert data["version"] == 2
