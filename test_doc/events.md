# Events and Venues API Component Test Documentation

## Overview
This document records the test coverage and verification status for the event and venue API work implemented in this chat.

## Test Cases Documented
1. `test_list_events_with_filters`
2. `test_get_event_detail_and_unauthorized_access`
3. `test_get_my_events_for_registered_and_participated`
4. `test_create_event_requires_admin_or_faculty`
5. `test_create_event_validation_errors`
6. `test_create_event_invalid_club_and_dates`
7. `test_update_event_and_status_permissions`
8. `test_update_event_rejects_invalid_dates`
9. `test_assign_venue_and_invalid_venue`
10. `test_assign_venue_requires_venue_id`
11. `test_register_and_fetch_registrations`
12. `test_manage_schedule_and_announcements`
13. `test_manage_schedule_and_announcements_validation_errors`
14. `test_manage_attendance_prizes_and_organizers`
15. `test_manage_prizes_and_organizers_listing`
16. `test_manage_volunteers_and_update_state`
17. `test_venues_listing_and_crud`
18. `test_venues_search_and_validation`

## Error Logged
- **Error Type**: `ValueError`
- **Location**: `backend/app/__init__.py`
- **Error Message**: `The name 'events' is already registered for this blueprint.`
- **Root Cause**: The event blueprint was being imported and registered twice during application startup.
- **Resolution**: Removed the duplicate import and registration so pytest could initialize the Flask app successfully.

## Resolution Plan
- Keep the event and venue API test suite focused on both success paths and validation/permission failures.
- Continue verifying the implementation with pytest after each major change to the API surface.

## Covered Endpoint Groups
- Event listing and detail retrieval: `GET /api/events`, `GET /api/events/<id>`
- My events lookup: `GET /api/events/me`
- Event creation and updates: `POST /api/events/create`, `PUT /api/events/<id>/edit`, `PATCH /api/events/<id>/status`
- Venue assignment: `POST /api/events/<id>/venue`
- Registrations: `POST /api/events/<id>/register`, `GET /api/events/<id>/registrations`
- Schedule and announcements: `POST/PUT /api/events/<id>/schedule`, `POST/PUT /api/events/<id>/announcements`
- Attendance, prizes, organizers: `GET/POST/PUT /api/events/<id>/attendance`, `GET/POST/PUT /api/events/<id>/prizes`, `GET/POST /api/events/<id>/organizers`
- Volunteers: `GET/POST /api/events/<id>/volunteers`, `PATCH /api/events/<id>/volunteers/<volunteer_id>`
- Venue CRUD: `GET /api/venues`, `GET /api/venues/<id>`, `POST /api/venues/create`, `PUT /api/venues/<id>/edit`, `PATCH /api/venues/<id>/status`