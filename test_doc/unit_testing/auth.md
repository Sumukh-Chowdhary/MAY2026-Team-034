# Authentication Component Test Documentation

## Overview
This document logs the test execution results, errors encountered, and resolutions for the `auth` component (`backend/tests/test_auth.py`).

## Test Cases Documented
1. `test_admin_login`
2. `test_faculty_login`
3. `test_student_login`
4. `test_login_by_roll_no`
5. `test_login_by_employee_id`
6. `test_login_missing_fields`
7. `test_login_invalid_password`
8. `test_login_non_existent_user`
9. `test_login_deactivated_user`
10. `test_register_student_success`
11. `test_register_faculty_success`
12. `test_register_missing_fields`
13. `test_register_duplicate_email`
14. `test_register_duplicate_roll_no`
15. `test_register_duplicate_employee_id`
16. `test_logout`
17. `test_change_password`
18. `test_change_password_failures`
19. `test_get_me`

## Error Logged
- **Error Type**: `NameError`
- **Location**: `backend/app/utils/seed.py:169`
- **Error Message**: `ERROR test_auth.py - NameError: name 'fac_user' is not defined`
- **Root Cause**: During test fixture database seeding (`seed_database`), `ClubFaculty` instantiation attempted to access `fac_user.id`, but `fac_user` variable was missing variable initialization from `faculty_lookup[club["faculty"]]`.

## Resolution Plan
Define `fac_user = faculty_lookup[club["faculty"]]` in `backend/app/utils/seed.py` before adding `ClubFaculty` records.
