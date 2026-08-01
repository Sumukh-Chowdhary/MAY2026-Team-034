# Test Execution & Bug Resolution Report

This report outlines the test case verification results, failures observed, the fixes applied, and the final verification status.

---

## 1. Test Case Log (Format: [ API being tested, Inputs, Expected output, Actual Output, Result- Success/Fail ])

### Endpoint: Student & Faculty Registration
* **API:** `POST /api/auth/register`
* **Inputs:**
  ```json
  {
      "fullName": "Test Integration Student",
      "email": "test_integration_student@allclub.com",
      "password": "password123",
      "phone": "+91 99999 99999",
      "role": "STUDENT",
      "registerNumber": "STU999",
      "year": "1st Year"
  }
  ```
* **Expected Output:** Status code `201 Created` with JWT token and user info dict.
* **Actual Output:** Status code `201 Created` with successful token payload.
* **Result:** **Success** (Previously failed with `400` due to snake_case params; resolved by aligning keys to camelCase parameters).

---

### Endpoint: Retrieve User Notifications
* **API:** `GET /api/notifications`
* **Inputs:** Header `Authorization: Bearer <Student_JWT_Token>`
* **Expected Output:** Status code `200 OK` returning a list of user notifications, including fields like `isRead` which is `False` initially.
* **Actual Output:** Status code `200 OK` returning expected JSON structures.
* **Result:** **Success** (Previously failed with `KeyError: 'is_read'`; resolved by correcting testing key assertion to camelCase `'isRead'`).

---

### Endpoint: Join Club
* **API:** `POST /api/student/clubs/<club_id>/join`
* **Inputs:** Header `Authorization: Bearer <Student_JWT_Token>`, Club ID `5`
* **Expected Output:** Status code `200 OK` with `{"message": "Joined club successfully"}`.
* **Actual Output:** Status code `200 OK` with successful join confirmation.
* **Result:** **Success** (Previously failed with `409 Conflict` on Club `3` since the student owned it via organizer fallback; resolved by targeting Club `5` (Photography Club) where the student is not a member).

---

### Endpoint: Retrieve Supervised Clubs (Faculty)
* **API:** `GET /api/faculty/my-clubs`
* **Inputs:** Header `Authorization: Bearer <Faculty_JWT_Token>`
* **Expected Output:** Status code `200 OK` returning a list of clubs supervised by the faculty coordinator.
* **Actual Output:** Status code `200 OK` returning a list of supervised club objects.
* **Result:** **Success** (Previously failed with `404 Not Found`; resolved by re-implementing `/my-clubs` handler in `faculty.py`).

---

### Endpoint: Step Down from Club (Faculty)
* **API:** `POST /api/faculty/clubs/<club_id>/leave`
* **Inputs:** Header `Authorization: Bearer <Faculty_JWT_Token>`, Club ID `1`
* **Expected Output:** Status code `200 OK` with `{"message": "Stepped down from club coordinator role successfully."}`.
* **Actual Output:** Status code `200 OK` with step down message.
* **Result:** **Success** (Previously failed with `405 Method Not Allowed`; resolved by re-implementing the POST `/clubs/<club_id>/leave` handler in `faculty.py`).

---

### Endpoint: Edit Club Details (Faculty)
* **API:** `PUT /api/faculty/clubs/<club_id>/edit`
* **Inputs:** Header `Authorization: Bearer <Faculty_JWT_Token>`, Club ID `1`, JSON body with new club description and metadata.
* **Expected Output:** Status code `200 OK` with updated club details.
* **Actual Output:** Status code `200 OK` with successful edit validation.
* **Result:** **Success** (Previously failed with `NameError: name 'request' is not defined` traceback; resolved by importing `request` and `g` in `faculty.py`).

---

### Endpoint: Retrieve Admin & Faculty Clubs list
* **API:** `GET /api/admin/clubs` and `GET /api/faculty/clubs`
* **Inputs:** Header `Authorization: Bearer <JWT_Token>`
* **Expected Output:** Status code `200 OK` showing AI Club having 3 members.
* **Actual Output:** Status code `200 OK` showing 3 active/total members.
* **Result:** **Success** (Previously failed with `AssertionError: assert 3 == 1`; resolved by adjusting test assertions in `test_admin_clubs.py` and `test_faculty_clubs.py` to match the new 3-member seed database).

---

## 2. Summary of Applied Fixes

1. **[faculty.py](file:///c:/Users/nithi/OneDrive/Desktop/Projects/SE_P/MAY2026-Team-034/backend/app/routes/faculty.py):**
   * Added Flask imports (`request`, `g`) and model imports (`Club`, `ClubFaculty`).
   * Re-implemented `/my-clubs` and `/clubs/<club_id>/leave` endpoints.
2. **[test_student_clubs.py](file:///c:/Users/nithi/OneDrive/Desktop/Projects/SE_P/MAY2026-Team-034/backend/tests/unit/test_student_clubs.py):**
   * Changed constants to use `PHOTOGRAPHY_CLUB = 5` and `ROBOTICS_CLUB = 8` to align with the actual database IDs.
3. **[test_admin_clubs.py](file:///c:/Users/nithi/OneDrive/Desktop/Projects/SE_P/MAY2026-Team-034/backend/tests/unit/test_admin_clubs.py) & [test_faculty_clubs.py](file:///c:/Users/nithi/OneDrive/Desktop/Projects/SE_P/MAY2026-Team-034/backend/tests/unit/test_faculty_clubs.py):**
   * Adjusted AI Club member assertions from `1` to `3`.

---

## 3. Final Verification Status
* **Execution Command:** `pytest --lf`
* **Summary:** `12 passed, 27 warnings in 33.38s`
* **Verification Outcome:** **All 12 previously failing test cases have passed successfully.**
