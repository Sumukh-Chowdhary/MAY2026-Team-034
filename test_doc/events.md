# Events and Venues API Test Documentation

## Overview
This document summarizes the covered API behavior for the event and venue endpoints implemented in the backend.

## Test Cases Documented
1. `test_list_events_with_filters`
2. `test_get_my_events_for_registered_and_participated`
3. `test_create_event_requires_admin_or_faculty`
4. `test_create_event_validation_errors`
5. `test_update_event_and_status_permissions`
6. `test_assign_venue_and_invalid_venue`
7. `test_register_and_fetch_registrations`
8. `test_manage_schedule_and_announcements`
9. `test_manage_attendance_prizes_and_organizers`
10. `test_manage_volunteers_and_update_state`
11. `test_venues_listing_and_crud`

## Covered Endpoint Groups
- Event listing and filtering: `GET /api/events`
- My events lookup: `GET /api/events/me`
- Event creation: `POST /api/events/create`
- Event update and status updates: `PUT /api/events/<id>/edit`, `PATCH /api/events/<id>/status`
- Venue assignment: `POST /api/events/<id>/venue`
- Registration management: `POST /api/events/<id>/register`, `GET /api/events/<id>/registrations`
- Schedule and announcements: `POST/PUT /api/events/<id>/schedule`, `POST/PUT /api/events/<id>/announcements`
- Attendance, prizes, organizers: `GET/POST/PUT /api/events/<id>/attendance`, `GET/POST/PUT /api/events/<id>/prizes`, `GET/POST /api/events/<id>/organizers`
- Volunteers: `POST /api/events/<id>/volunteers`, `PATCH /api/events/<id>/volunteers/<volunteer_id>`
- Venue CRUD: `GET /api/venues`, `GET /api/venues/<id>`, `POST /api/venues/create`, `PUT /api/venues/<id>/edit`, `PATCH /api/venues/<id>/status`

## Notes
These tests validate both success paths and permission/validation handling for the new event and venue API surface.