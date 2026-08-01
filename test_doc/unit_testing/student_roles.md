# Student Roles Component Test Documentation

## Overview
This document logs the test execution results, errors encountered, and resolutions for the `student_roles` component (`backend/tests/test_student_roles.py`).

## Test Cases Documented
1. `test_get_user_assignments`
2. `test_get_user_assignments_unauthorized`
3. `test_create_role_request`
4. `test_student_leave_assignment_ticket`
5. `test_student_leave_assignment_invalid_id`

## Error Logged
- **Error Type**: `NameError`
- **Location**: `backend/app/utils/seed.py:169`
- **Error Message**: `ERROR test_student_roles.py - NameError: name 'fac_user' is not defined`
- **Root Cause**: Pytest fixture `app` failed during test initialization due to undefined `fac_user` variable in database seeder.

## Resolution Plan
Correct `seed.py` by adding `fac_user = faculty_lookup[club["faculty"]]`.
