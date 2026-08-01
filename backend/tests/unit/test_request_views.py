import pytest

def test_student_dashboard(client, student_headers):
    """Test student dashboard aggregation."""
    res = client.get("/api/student/requests/dashboard", headers=student_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "myTickets" in data
    assert isinstance(data["myTickets"], list)

def test_student_dashboard_unauthorized(client, faculty_headers):
    """Test faculty accessing student dashboard."""
    res = client.get("/api/student/requests/dashboard", headers=faculty_headers)
    assert res.status_code == 403

def test_faculty_dashboard(client, faculty_headers):
    """Test faculty dashboard aggregation."""
    res = client.get("/api/faculty/requests/dashboard", headers=faculty_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "myTickets" in data
    assert "incomingRequests" in data
    assert isinstance(data["myTickets"], list)
    assert isinstance(data["incomingRequests"], list)

def test_faculty_dashboard_unauthorized(client, student_headers):
    """Test student accessing faculty dashboard."""
    res = client.get("/api/faculty/requests/dashboard", headers=student_headers)
    assert res.status_code == 403

def test_admin_dashboard(client, admin_headers):
    """Test admin dashboard aggregation."""
    res = client.get("/api/admin/requests/dashboard", headers=admin_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "clubRequests" in data
    assert "eventRequests" in data
    assert isinstance(data["clubRequests"], list)
    assert isinstance(data["eventRequests"], list)

def test_admin_dashboard_unauthorized(client, faculty_headers):
    """Test faculty accessing admin dashboard."""
    res = client.get("/api/admin/requests/dashboard", headers=faculty_headers)
    assert res.status_code == 403
