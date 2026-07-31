# Student Clubs Component Test Documentation

## Overview
This document logs the test execution results, errors encountered, and resolutions for the `student_clubs` component (`backend/tests/test_student_clubs.py`).

## Test Cases Documented
1. `test_get_clubs`
2. `test_get_my_clubs`
3. `test_join_club`
4. `test_leave_club`
5. `test_duplicate_leave_club`
6. `test_invalid_join_club`
7. `test_invalid_leave_club`
8. `test_admin_cannot_join_club`
9. `test_faculty_cannot_join_club`
10. `test_unauthenticated_request`
11. `test_invalid_token`
12. `test_incremented_membercounts`

## Error Logged
- **Error 1**: `NameError`
  - **Location**: `backend/app/utils/seed.py:169`
  - **Error Message**: `ERROR test_student_clubs.py - NameError: name 'fac_user' is not defined`
  - **Root Cause**: Database setup error caused by missing `fac_user` variable assignment when populating `ClubFaculty`.
  - **Resolution**: Set `fac_user = faculty_lookup[club["faculty"]]` in `backend/app/utils/seed.py`.

- **Error 2**: `KeyError`
  - **Location**: `backend/app/utils/seed.py:175` & `backend/app/utils/seed_data.py:141`
  - **Error Message**: `ERROR test_student_clubs.py - KeyError: 'STU010'`
  - **Root Cause**: `CLUB_DATA` referenced an unseeded roll number (`STU010`) which did not exist in `STUDENT_DATA`.
  - **Resolution**: Updated `seed_data.py` to use `STU004` and added safe lookup fallback (`student_lookup.get(...) or student_users[0]`) in `seed.py`.

- **Error 3**: `KeyError`
  - **Location**: `backend/app/utils/seed.py:156` & `backend/app/utils/seed_data.py:151-205`
  - **Error Message**: `ERROR test_student_clubs.py - KeyError: 'category'`
  - **Root Cause**: `CLUB_DATA` contained duplicated event objects which lacked a `"category"` key required for `Club` creation.
  - **Resolution**: Removed duplicated event objects from `CLUB_DATA` in `seed_data.py` and added a `"category"` key presence guard check in `seed.py`.

- **Error 4**: `NameError` & `Index Lookup`
  - **Location**: `backend/tests/test_student_clubs.py` (Lines 141-205)
  - **Error Message**: `NameError: name 'MUSIC_CLUB' is not defined`
  - **Root Cause**: Unused constant `MUSIC_CLUB` remained in join endpoints; static index lookup `clubs[2]` failed assertion.
  - **Resolution**: Replaced `MUSIC_CLUB` with `ROBOTICS_CLUB` (ID 2) and changed list access to `next(c for c in clubs if c["id"] == PHOTOGRAPHY_CLUB)`. All 12 test cases now pass.
