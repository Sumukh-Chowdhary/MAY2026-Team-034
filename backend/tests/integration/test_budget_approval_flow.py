import pytest
from app.models.tickets import Request, RequestApproval, ApprovalStatus

def test_budget_request_multi_level_approval_integration(client, app, student_headers, faculty_headers, admin_headers):
    # 1. Student creates a BUDGET_REQUEST referencing Club ID 1
    create_response = client.post(
        "/api/requests",
        headers=student_headers,
        json={
            "requestType": "BUDGET_REQUEST",
            "title": "Annual Tech Fest Budget Request",
            "description": "Requesting 75,000 INR for hackathon logistics and prizes",
            "referenceType": "CLUB",
            "referenceId": 1
        }
    )
    assert create_response.status_code == 201
    request_data = create_response.get_json()["data"]
    request_id = request_data["id"]
    
    # Verify the initial workflow status is PENDING
    assert request_data["workflowStatus"] == ApprovalStatus.PENDING
    
    # 2. Verify that three approvals were generated for the request
    approvals = request_data["approvals"]
    assert len(approvals) == 3
    
    # Check the roles in the approval chain
    roles = {appr["approvalRole"] for appr in approvals}
    assert "CLUB_FACULTY" in roles
    assert "PRINCIPAL" in roles
    assert "ADMIN" in roles
    
    # 3. Faculty Coordinator approves (Meena - user ID 3)
    faculty_approval_resp = client.post(
        f"/api/requests/{request_id}/approve",
        headers=faculty_headers,
        json={"remarks": "Recommended. The budget is justified."}
    )
    assert faculty_approval_resp.status_code == 200
    
    # The request should still be PENDING since HOD/Principal and Admin haven't approved
    assert faculty_approval_resp.get_json()["data"]["workflowStatus"] == ApprovalStatus.PENDING

    # 4. Principal approves (Dr. K. S. Murthy - user ID 2)
    # First get principal headers
    principal_login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "principal@allclub.com",
            "password": "principal123"
        }
    )
    assert principal_login_resp.status_code == 200
    principal_token = principal_login_resp.get_json()["token"]
    principal_headers = {"Authorization": f"Bearer {principal_token}"}
    
    principal_approval_resp = client.post(
        f"/api/requests/{request_id}/approve",
        headers=principal_headers,
        json={"remarks": "Approved from Principal Office."}
    )
    assert principal_approval_resp.status_code == 200
    assert principal_approval_resp.get_json()["data"]["workflowStatus"] == ApprovalStatus.PENDING

    # 5. Admin approves (Admin - user ID 1)
    admin_approval_resp = client.post(
        f"/api/requests/{request_id}/approve",
        headers=admin_headers,
        json={"remarks": "Budget sanctioned."}
    )
    assert admin_approval_resp.status_code == 200
    
    # Once the last pending approver in the chain signs off, the request becomes APPROVED
    assert admin_approval_resp.get_json()["data"]["workflowStatus"] == ApprovalStatus.APPROVED
