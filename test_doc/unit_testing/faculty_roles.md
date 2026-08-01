# Faculty Roles Component Test Documentation

## Overview
This document logs the test execution results, errors encountered, and resolutions for the `faculty_roles` component (`backend/tests/test_faculty_roles.py`).

## Test Cases Documented
1. `test_get_my_supervised_clubs`
2. `test_get_my_supervised_clubs_unauthorized`
3. `test_faculty_requests_dashboard`
4. `test_leave_faculty_role`
5. `test_leave_faculty_role_invalid_club`

## Error Logged
- **Error Type**: `NameError`
- **Location**: `backend/app/utils/seed.py:169`
- **Error Message**: `ERROR test_faculty_roles.py - NameError: name 'fac_user' is not defined`
- **Root Cause**: Database setup fixture failed because `seed.py` referenced `fac_user.id` without looking up `faculty_lookup[club["faculty"]]`.

## Resolution Plan
Fix the `fac_user` variable assignment in `backend/app/utils/seed.py`.
