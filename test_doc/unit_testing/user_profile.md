# User Profile Component Test Documentation

## Overview
This document logs the test execution results, errors encountered, and resolutions for the `user_profile` component (`backend/tests/test_user_profile.py`).

## Test Cases Documented
1. `test_get_user_profile`
2. `test_update_self_profile`
3. `test_update_other_user_profile_forbidden`
4. `test_admin_update_any_user_profile`

## Errors & Alignments Logged
- **Error 1**: `NameError`
  - **Location**: `backend/app/utils/seed.py:169`
  - **Error Message**: `ERROR test_user_profile.py - NameError: name 'fac_user' is not defined`
  - **Root Cause**: Database setup error caused by missing `fac_user` variable assignment in `seed.py`.
  - **Resolution**: Defined `fac_user = faculty_lookup[club["faculty"]]` in `seed.py`.

- **Alignment Fix 2**: `User ID Mapping`
  - **Location**: `backend/tests/test_user_profile.py`
  - **Details**: Updated test assertions to match seeded user IDs: Dr. Meena Rao (`meena@allclub.com`) is user ID 3 (ID 2 is Principal), and Rahul Sharma is user ID 6. All tests now pass cleanly with 200 OK responses.
