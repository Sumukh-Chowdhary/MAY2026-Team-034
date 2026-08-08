ADMIN_DATA = {
    "email": "admin@allclub.com",
    "password": "admin123",
    "roll_no": "ADM001",
    "full_name": "Admin User",
    "phone_number": "+91 90000 00001",
    "year_of_study": None,
    "department": "ADM",
    "bio": "Platform administrator managing all clubs, events, and users."
}

FACULTY_DATA = [
    {
        "email": "principal@allclub.com",
        "password": "principal123",
        "employee_id": "PRIN001",
        "full_name": "Dr. K. S. Murthy (Principal)",
        "phone_number": "+91 90000 00000",
        "department": "ADM",
        "designation": "PRINCIPAL",
        "bio": "Principal of the institution overseeing overall academic and extra-curricular administration."
    },
    {
        "email": "meena@allclub.com",
        "password": "faculty123",
        "employee_id": "FAC001",
        "full_name": "Dr. Meena Rao",
        "phone_number": "+91 90000 00002",
        "department": "CSE",
        "designation": "Associate Professor",
        "bio": "Faculty advisor. Passionate about machine learning research."
    },
    {
        "email": "arjun@allclub.com",
        "password": "faculty123",
        "employee_id": "FAC002",
        "full_name": "Dr. Arjun Nair",
        "phone_number": "+91 90000 00004",
        "department": "ECE",
        "designation": "Assistant Professor",
        "bio": "Faculty advisor for Robotics and Electronics clubs."
    },
    {
        "email": "priya@allclub.com",
        "password": "faculty123",
        "employee_id": "FAC003",
        "full_name": "Dr. Priya Iyer",
        "phone_number": "+91 90000 00005",
        "department": "CSE",
        "designation": "Professor",
        "bio": "Researcher in Artificial Intelligence and Data Science."
    }
]

STUDENT_DATA = [
    {
        "email": "rahul@allclub.com",
        "password": "student123",
        "roll_no": "STU001",
        "full_name": "Rahul Sharma",
        "phone_number": "+91 90000 00003",
        "year_of_study": "3rd Year",
        "department": "CSE",
        "bio": "Computer science student interested in web development."
    },
    {
        "email": "ananya@allclub.com",
        "password": "student123",
        "roll_no": "STU002",
        "full_name": "Ananya Gupta",
        "phone_number": "+91 90000 00006",
        "year_of_study": "2nd Year",
        "department": "CSE",
        "bio": "Enjoys UI/UX design and student activities."
    },
    {
        "email": "vikram@allclub.com",
        "password": "student123",
        "roll_no": "STU003",
        "full_name": "Vikram Singh",
        "phone_number": "+91 90000 00007",
        "year_of_study": "4th Year",
        "department": "ECE",
        "bio": "Electronics enthusiast and robotics hobbyist."
    },
    {
        "email": "sneha@allclub.com",
        "password": "student123",
        "roll_no": "STU004",
        "full_name": "Sneha Nair",
        "phone_number": "+91 90000 00008",
        "year_of_study": "1st Year",
        "department": "CSE",
        "bio": "Interested in theatre and public speaking."
    },
    {
        "email": "karthik@allclub.com",
        "password": "student123",
        "roll_no": "STU005",
        "full_name": "Karthik Rao",
        "phone_number": "+91 90000 00009",
        "year_of_study": "3rd Year",
        "department": "ECE",
        "bio": "Passionate about embedded systems."
    },
    {
        "email": "meera@allclub.com",
        "password": "student123",
        "roll_no": "STU006",
        "full_name": "Meera Das",
        "phone_number": "+91 90000 00010",
        "year_of_study": "2nd Year",
        "department": "CSE",
        "bio": "Aspirant software developer."
    }
]

CLUB_DATA = [
    {
        "name": "AI Club",
        "description": "Learn Artificial Intelligence and Machine Learning together.",
        "category": "Technology",
        "logo": "psychology",
        "faculty": "FAC001",
        "organizer": "STU001",
    },
    {
        "name": "Music Club",
        "description": "Jam sessions, performances and music workshops.",
        "category": "Arts",
        "logo": "music_note",
        "faculty": "FAC003",
        "organizer": "STU010"
    },
    {
        "name": "Sports Club",
        "description": "Football, Cricket, Basketball and many more activities.",
        "category": "Sports",
        "logo": "sports_soccer",
        "faculty": "FAC002",
        "organizer": "STU009"
    },
    {
        "name": "Drama Club",
        "description": "Theatre performances, acting practice and stage events.",
        "category": "Cultural",
        "logo": "theater_comedy",
        "faculty": "FAC003",
        "organizer": "STU014"
    },
    {
        "name": "Photography Club",
        "description": "Capture moments and learn photography together.",
        "category": "Creative",
        "logo": "photo_camera",
        "faculty": "FAC001",
        "organizer": "STU006"
    },
    {
        "name": "Science Club",
        "description": "Science projects, exhibitions and research discussions.",
        "category": "Academic",
        "logo": "science",
        "faculty": "FAC002",
        "organizer": "STU015"
    },
    {
        "name": "Coding Club",
        "description": "Fostering programming, algorithmic thinking, and open source development across campus.",
        "category": "TECHNICAL",
        "logo": "terminal",
        "faculty": "FAC001",
        "organizer": "STU001"
    },
    {
        "name": "Robotics Club",
        "description": "Building autonomous bots, IoT systems, and competing in national hardware hackathons.",
        "category": "TECHNICAL",
        "logo": "smart_toy",
        "faculty": "FAC001",
        "organizer": "STU001"
    }
]

VENUE_DATA = [
    {
        "name": "Main Auditorium",
        "location": "Block A, 2nd Floor",
        "type": "Auditorium",
        "capacity": 250,
        "availabilityStatus": "AVAILABLE"
    },
    {
        "name": "Innovation Lab",
        "location": "Block C, Lab 3",
        "type": "Lab",
        "capacity": 80,
        "availabilityStatus": "OCCUPIED"
    },
    {
        "name": "Open Air Ground",
        "location": "North Campus",
        "type": "Ground",
        "capacity": 400,
        "availabilityStatus": "AVAILABLE"
    },
    {
        "name": "Studio Hall",
        "location": "Arts Block, Floor 1",
        "type": "Hall",
        "capacity": 120,
        "availabilityStatus": "AVAILABLE"
    },
    {
        "name": "Seminar Room 101",
        "location": "Block B, Floor 1",
        "type": "Classroom",
        "capacity": 60,
        "availabilityStatus": "AVAILABLE"
    },
    {
        "name": "Conference Hall Alpha",
        "location": "Admin Block, Floor 3",
        "type": "Conference Room",
        "capacity": 150,
        "availabilityStatus": "ARCHIVED"
    }
]

EVENT_DATA = [
    {
        "organizerType": "CLUB",
        "clubName": "AI Club",
        "createdByEmail": "meena@allclub.com",
        "name": "AI Hack Sprint",
        "description": "A full-day coding sprint focused on AI prototypes and demos.",
        "status": "LIVE",
        "startDate": "2026-08-07",
        "endDate": "2026-08-09",
        "startTime": "09:00:00",
        "endTime": "17:00:00",
        "capacity": 80,
        "venueName": "Innovation Lab",
        "schedule": [
            {"time": "09:00", "activity": "Registration and setup"},
            {"time": "10:00", "activity": "Opening keynote"},
            {"time": "13:00", "activity": "Hackathon round 1"}
        ],
        "announcements": [
            {"title": "Bring your laptop", "message": "Please carry your laptop and charger for the sprint."}
        ],
        "registrations": ["rahul@allclub.com", "ananya@allclub.com", "aditya@allclub.com"],
        "attendance": ["rahul@allclub.com", "ananya@allclub.com"],
        "prizes": [
            {"title": "Best Innovation", "winnerEmail": "aditya@allclub.com", "description": "Most practical AI prototype"}
        ],
        "organizers": ["rahul@allclub.com"],
        "volunteers": ["sneha@allclub.com", "karthik@allclub.com"]
    },
    {
        "organizerType": "GENERAL",
        "clubName": None,
        "createdByEmail": "meena@allclub.com",
        "name": "Freshers Campus Orientation 2026",
        "description": "Welcome ceremony and campus orientation for the incoming batch of 2026.",
        "status": "SCHEDULED",
        "startDate": "2026-08-15",
        "endDate": "2026-08-15",
        "startTime": "09:30:00",
        "endTime": "13:00:00",
        "capacity": 500,
        "venueName": "Main Auditorium",
        "schedule": [
            {"time": "09:30", "activity": "Welcome speech by Principal"},
            {"time": "11:00", "activity": "Academic orientation and campus tour"}
        ],
        "announcements": [
            {"title": "Welcome Students", "message": "All first-year students must attend in formal attire."}
        ],
        "registrations": ["rahul@allclub.com", "ananya@allclub.com"],
        "attendance": ["rahul@allclub.com"],
        "prizes": [],
        "organizers": [],
        "volunteers": []
    },
    {
        "organizerType": "GENERAL",
        "clubName": None,
        "createdByEmail": "principal@allclub.com",
        "name": "15th Annual College Convocation",
        "description": "Graduation ceremony honoring the graduating class of 2026.",
        "status": "SCHEDULED",
        "startDate": "2026-09-10",
        "endDate": "2026-09-10",
        "startTime": "10:00:00",
        "endTime": "16:00:00",
        "capacity": 800,
        "venueName": "Main Auditorium",
        "schedule": [
            {"time": "10:00", "activity": "Procession and Commencement Speech"},
            {"time": "12:30", "activity": "Degree Distribution"}
        ],
        "announcements": [],
        "registrations": [],
        "attendance": [],
        "prizes": [],
        "organizers": [],
        "volunteers": []
    },
    {
        "organizerType": "GENERAL",
        "clubName": None,
        "createdByEmail": "arjun@allclub.com",
        "name": "Mega Campus Placement Drive 2026",
        "description": "Annual placement drive connecting top technology firms with graduating students.",
        "status": "SCHEDULED",
        "startDate": "2026-09-25",
        "endDate": "2026-09-27",
        "startTime": "09:00:00",
        "endTime": "17:30:00",
        "capacity": 600,
        "venueName": "Seminar Hall A",
        "schedule": [],
        "announcements": [],
        "registrations": ["rahul@allclub.com"],
        "attendance": [],
        "prizes": [],
        "organizers": [],
        "volunteers": []
    },
    {
        "organizerType": "GENERAL",
        "clubName": None,
        "createdByEmail": "priya@allclub.com",
        "name": "Annual Campus Blood Donation Drive",
        "description": "College-wide blood donation camp organized in partnership with Red Cross.",
        "status": "SCHEDULED",
        "startDate": "2026-08-28",
        "endDate": "2026-08-28",
        "startTime": "09:00:00",
        "endTime": "16:00:00",
        "capacity": 300,
        "venueName": "Open Air Ground",
        "schedule": [],
        "announcements": [],
        "registrations": [],
        "attendance": [],
        "prizes": [],
        "organizers": [],
        "volunteers": []
    },
    {
        "clubName": "Drama Club",
        "createdByEmail": "priya@allclub.com",
        "name": "Stagecraft Workshop",
        "description": "An interactive workshop covering stage direction, acting, and audience engagement.",
        "status": "SCHEDULED",
        "startDate": "2026-08-20",
        "endDate": "2026-08-20",
        "startTime": "14:00:00",
        "endTime": "18:00:00",
        "capacity": 120,
        "venueName": "Studio Hall",
        "schedule": [
            {"time": "14:00", "activity": "Welcome and icebreaker"},
            {"time": "15:30", "activity": "Scene rehearsal"},
            {"time": "17:00", "activity": "Feedback session"}
        ],
        "announcements": [
            {"title": "Workshop reminder", "message": "Participants should arrive 15 minutes early."}
        ],
        "registrations": ["kavya@allclub.com", "nisha@allclub.com"],
        "attendance": ["kavya@allclub.com"],
        "prizes": [],
        "organizers": ["kavya@allclub.com"],
        "volunteers": ["neeraj@allclub.com"]
    },
    {
        "clubName": "Sports Club",
        "createdByEmail": "arjun@allclub.com",
        "name": "Inter-Club Sports Day",
        "description": "A fun-filled sports event featuring football, basketball, and relay competitions.",
        "status": "SCHEDULED",
        "startDate": "2026-09-05",
        "endDate": "2026-09-06",
        "startTime": "08:00:00",
        "endTime": "18:00:00",
        "capacity": 400,
        "venueName": "Open Air Ground",
        "schedule": [
            {"time": "08:00", "activity": "Opening ceremony"},
            {"time": "10:00", "activity": "Football matches"},
            {"time": "15:00", "activity": "Awards and closing"}
        ],
        "announcements": [
            {"title": "Team registration", "message": "Team captains should confirm their roster by Friday."}
        ],
        "registrations": ["aman@allclub.com", "rohan@allclub.com", "vikram@allclub.com"],
        "attendance": ["aman@allclub.com"],
        "prizes": [
            {"title": "Best Team Spirit", "winnerEmail": "rohan@allclub.com", "description": "Recognized for teamwork and sportsmanship"}
        ],
        "organizers": ["aman@allclub.com"],
        "volunteers": ["vikram@allclub.com", "ishita@allclub.com"]
    },
    {
        "clubName": "Robotics Club",
        "createdByEmail": "arjun@allclub.com",
        "name": "Robotics Hardware Expo",
        "description": "Exhibition of autonomous rovers and IoT hardware prototypes.",
        "status": "SCHEDULED",
        "startDate": "2026-09-12",
        "endDate": "2026-09-14",
        "startTime": "10:00:00",
        "endTime": "16:00:00",
        "capacity": 80,
        "venueName": "Innovation Lab",
        "schedule": [
            {"time": "10:00", "activity": "Project Demonstration"},
            {"time": "14:00", "activity": "Hardware Testing"}
        ],
        "announcements": [],
        "registrations": ["vikram@allclub.com"],
        "attendance": [],
        "prizes": [],
        "organizers": ["vikram@allclub.com"],
        "volunteers": []
    },
    {
        "clubName": "Photography Club",
        "createdByEmail": "meena@allclub.com",
        "name": "Campus Gallery Exhibition",
        "description": "Exhibition showcasing winning photographs from campus photo walks.",
        "status": "SCHEDULED",
        "startDate": "2026-10-02",
        "endDate": "2026-10-03",
        "startTime": "11:00:00",
        "endTime": "17:00:00",
        "capacity": 120,
        "venueName": "Studio Hall",
        "schedule": [],
        "announcements": [],
        "registrations": ["meera@allclub.com"],
        "attendance": [],
        "prizes": [],
        "organizers": ["meera@allclub.com"],
        "volunteers": []
    },
    {
        "clubName": "Coding Club",
        "createdByEmail": "karthik@allclub.com",
        "name": "Summer Code Sprint 2026",
        "description": "Completed algorithm speedrun and competitive programming challenge.",
        "status": "COMPLETED",
        "startDate": "2026-07-15",
        "endDate": "2026-07-16",
        "startTime": "10:00:00",
        "endTime": "16:00:00",
        "capacity": 250,
        "venueName": "Main Auditorium",
        "schedule": [
            {"time": "10:00", "activity": "Contest Kickoff"},
            {"time": "15:00", "activity": "Leaderboard Freeze"},
            {"time": "16:00", "activity": "Prize Distribution"}
        ],
        "announcements": [
            {"title": "Sprint Completed", "message": "Thanks to all participants for competing!"}
        ],
        "registrations": ["karthik@allclub.com", "rahul@allclub.com"],
        "attendance": ["karthik@allclub.com", "rahul@allclub.com"],
        "prizes": [
            {"title": "1st Place", "winnerEmail": "karthik@allclub.com", "description": "Champion programmer"}
        ],
        "organizers": ["karthik@allclub.com"],
        "volunteers": []
    }
]

MEMBERSHIP_SEED_DATA = [
    {"club_id": 1, "user_id": 6, "membership_role": "PRESIDENT", "membership_status": "ACTIVE"},
    {"club_id": 1, "user_id": 7, "membership_role": "ORGANIZER", "membership_status": "ACTIVE"},
    {"club_id": 1, "user_id": 8, "membership_role": "MEMBER", "membership_status": "ACTIVE"},
    {"club_id": 2, "user_id": 6, "membership_role": "ORGANIZER", "membership_status": "ACTIVE"},
    {"club_id": 2, "user_id": 9, "membership_role": "MEMBER", "membership_status": "ACTIVE"},
    {"club_id": 2, "user_id": 10, "membership_role": "MEMBER", "membership_status": "INACTIVE"},
    {"club_id": 3, "user_id": 9, "membership_role": "PRESIDENT", "membership_status": "ACTIVE"},
    {"club_id": 3, "user_id": 11, "membership_role": "MEMBER", "membership_status": "ACTIVE"},
    {"club_id": 3, "user_id": 7, "membership_role": "VOLUNTEER", "membership_status": "ACTIVE"},
    {"club_id": 4, "user_id": 8, "membership_role": "PRESIDENT", "membership_status": "ACTIVE"},
    {"club_id": 4, "user_id": 10, "membership_role": "VOLUNTEER", "membership_status": "ACTIVE"},
    {"club_id": 4, "user_id": 11, "membership_role": "MEMBER", "membership_status": "ACTIVE"}
]

REQUEST_SEED_DATA = [
    {
        "requesterEmail": "rahul@allclub.com",
        "requestType": "CREATE_EVENT_AS_ORGANIZER",
        "title": "AI Ethics & Governance Panel",
        "description": "Panel discussion on responsible AI and policy frameworks in tech.",
        "referenceType": "CLUB",
        "referenceName": "AI Club",
        "priority": "HIGH",
        "workflowStatus": "APPROVED",
        "approvals": [
            {"approverEmail": "meena@allclub.com", "approvalRole": "CLUB_FACULTY", "approvalOrder": 1, "status": "APPROVED", "remarks": "Approved. Important topic."}
        ]
    },
    {
        "requesterEmail": "ananya@allclub.com",
        "requestType": "BECOME_ORGANIZER",
        "title": "Apply for Music Club Event Lead",
        "description": "Requesting organizer permissions to coordinate weekend jam sessions.",
        "referenceType": "CLUB",
        "referenceName": "Music Club",
        "priority": "MEDIUM",
        "workflowStatus": "PENDING",
        "approvals": [
            {"approverEmail": "priya@allclub.com", "approvalRole": "CLUB_FACULTY", "approvalOrder": 1, "status": "APPROVED", "remarks": "Strong candidate."},
            {"approverEmail": "admin@allclub.com", "approvalRole": "ADMIN", "approvalOrder": 2, "status": "PENDING", "remarks": None}
        ]
    },
    {
        "requesterEmail": "vikram@allclub.com",
        "requestType": "VENUE_REQUEST",
        "title": "Robotics Arena Ground Reservation",
        "description": "Requesting Open Air Ground for outdoor drone testing.",
        "referenceType": "CLUB",
        "referenceName": "Robotics Club",
        "priority": "HIGH",
        "workflowStatus": "CHANGES_REQUESTED",
        "approvals": [
            {"approverEmail": "arjun@allclub.com", "approvalRole": "CLUB_FACULTY", "approvalOrder": 1, "status": "CHANGES_REQUESTED", "remarks": "Please select an indoor venue or adjust date due to rain forecast."}
        ]
    },
    {
        "requesterEmail": "sneha@allclub.com",
        "requestType": "BECOME_VOLUNTEER",
        "title": "Volunteer Application for Drama Club",
        "description": "Application to join as stage management and lighting volunteer.",
        "referenceType": "CLUB",
        "referenceName": "Drama Club",
        "priority": "LOW",
        "workflowStatus": "APPROVED",
        "approvals": [
            {"approverEmail": "priya@allclub.com", "approvalRole": "CLUB_FACULTY", "approvalOrder": 1, "status": "APPROVED", "remarks": "Welcome to the team!"}
        ]
    },
    {
        "requesterEmail": "arjun@allclub.com",
        "requestType": "EDIT_CLUB_AS_COORDINATOR",
        "title": "Sports Club Description and Asset Update",
        "description": "Update sports club banners, training hours, and equipment details.",
        "referenceType": "CLUB",
        "referenceName": "Sports Club",
        "priority": "MEDIUM",
        "workflowStatus": "APPROVED",
        "approvals": [
            {"approverEmail": "admin@allclub.com", "approvalRole": "ADMIN", "approvalOrder": 1, "status": "APPROVED", "remarks": "Updated successfully."}
        ]
    },
    {
        "requesterEmail": "karthik@allclub.com",
        "requestType": "BUDGET_REQUEST",
        "title": "Hackathon Prize Pool Funding Request",
        "description": "Requesting $500 sponsorship for national coding challenge prizes.",
        "referenceType": "CLUB",
        "referenceName": "Coding Club",
        "priority": "HIGH",
        "workflowStatus": "REJECTED",
        "approvals": [
            {"approverEmail": "principal@allclub.com", "approvalRole": "PRINCIPAL", "approvalOrder": 1, "status": "REJECTED", "remarks": "Budget request exceeds departmental limit for Q3."}
        ]
    },
    {
        "requesterEmail": "meena@allclub.com",
        "requestType": "BECOME_FACULTY_COORDINATOR",
        "title": "Faculty Coordinator Application for Science Club",
        "description": "Faculty advisor nomination to lead student research projects.",
        "referenceType": "CLUB",
        "referenceName": "Science Club",
        "priority": "MEDIUM",
        "workflowStatus": "APPROVED",
        "approvals": [
            {"approverEmail": "admin@allclub.com", "approvalRole": "ADMIN", "approvalOrder": 1, "status": "APPROVED", "remarks": "Assigned as coordinator."}
        ]
    },
    {
        "requesterEmail": "meera@allclub.com",
        "requestType": "SCHEDULE_REQUEST",
        "title": "Night Photography Expedition Schedule Approval",
        "description": "Proposing campus night walk for long-exposure photography tutorial.",
        "referenceType": "CLUB",
        "referenceName": "Photography Club",
        "priority": "MEDIUM",
        "workflowStatus": "PENDING",
        "approvals": [
            {"approverEmail": "meena@allclub.com", "approvalRole": "CLUB_FACULTY", "approvalOrder": 1, "status": "PENDING", "remarks": None}
        ]
    }
]

ACTION_TICKET_SEED_DATA = [
    {
        "raisedByEmail": "rahul@allclub.com",
        "ticketType": "CREATE_CLUB",
        "title": "Propose CyberSecurity & Ethical Hacking Guild",
        "description": "Requesting creation of a student guild dedicated to CTFs and security research.",
        "priority": "HIGH",
        "approvalStatus": "APPROVED",
        "assignedToEmail": "admin@allclub.com",
        "taskStatus": "IN_PROGRESS",
        "dueDate": "2026-08-25",
        "completionRemarks": None,
        "approvals": [
            {"approverEmail": "meena@allclub.com", "approvalRole": "FACULTY_COORDINATOR", "approvalOrder": 1, "status": "APPROVED", "remarks": "Great initiative."},
            {"approverEmail": "admin@allclub.com", "approvalRole": "ADMIN", "approvalOrder": 2, "status": "APPROVED", "remarks": "Approved for creation."}
        ]
    },
    {
        "raisedByEmail": "arjun@allclub.com",
        "ticketType": "CREATE_EVENT_GENERAL",
        "title": "Annual Inter-College Tech Fest 2026",
        "description": "Proposal for institution-wide mega technology symposium.",
        "priority": "HIGH",
        "approvalStatus": "APPROVED",
        "assignedToEmail": "admin@allclub.com",
        "taskStatus": "OPEN",
        "dueDate": "2026-09-01",
        "completionRemarks": None,
        "approvals": [
            {"approverEmail": "principal@allclub.com", "approvalRole": "PRINCIPAL", "approvalOrder": 1, "status": "APPROVED", "remarks": "Approved at administrative level."},
            {"approverEmail": "admin@allclub.com", "approvalRole": "ADMIN", "approvalOrder": 2, "status": "APPROVED", "remarks": "Scheduled."}
        ]
    },
    {
        "raisedByEmail": "ananya@allclub.com",
        "ticketType": "CREATE_EVENT_FOR_CLUB",
        "title": "Acoustic Unplugged Evening",
        "description": "Inter-department acoustic music performance on student lounge lawn.",
        "priority": "MEDIUM",
        "approvalStatus": "PENDING",
        "assignedToEmail": None,
        "taskStatus": None,
        "dueDate": None,
        "completionRemarks": None,
        "approvals": [
            {"approverEmail": "priya@allclub.com", "approvalRole": "CLUB_FACULTY", "approvalOrder": 1, "status": "PENDING", "remarks": None}
        ]
    },
    {
        "raisedByEmail": "vikram@allclub.com",
        "ticketType": "EDIT_CLUB_ADMIN",
        "title": "Update Robotics Club Logo & Equipment Bio",
        "description": "Action item to update logo icon to smart_toy and list new 3D printers.",
        "priority": "LOW",
        "approvalStatus": "APPROVED",
        "assignedToEmail": "admin@allclub.com",
        "taskStatus": "COMPLETED",
        "dueDate": "2026-08-05",
        "completionRemarks": "Updated club profile details successfully.",
        "closedAt": "2026-08-05T14:30:00",
        "approvals": [
            {"approverEmail": "admin@allclub.com", "approvalRole": "ADMIN", "approvalOrder": 1, "status": "APPROVED", "remarks": "Completed."}
        ]
    },
    {
        "raisedByEmail": "sneha@allclub.com",
        "ticketType": "CREATE_CLUB",
        "title": "Propose Literary & Debate Society",
        "description": "Establish a formal parliamentary debate and creative writing society.",
        "priority": "MEDIUM",
        "approvalStatus": "CHANGES_REQUESTED",
        "assignedToEmail": None,
        "taskStatus": None,
        "dueDate": None,
        "completionRemarks": None,
        "approvals": [
            {"approverEmail": "priya@allclub.com", "approvalRole": "FACULTY_COORDINATOR", "approvalOrder": 1, "status": "CHANGES_REQUESTED", "remarks": "Need detailed faculty endorsement letter and budget outline."}
        ]
    },
    {
        "raisedByEmail": "priya@allclub.com",
        "ticketType": "EDIT_EVENT_ADMIN",
        "title": "Reschedule Stagecraft Workshop Venue",
        "description": "Re-allocate Stagecraft Workshop from Main Hall to Studio Hall.",
        "priority": "HIGH",
        "approvalStatus": "APPROVED",
        "assignedToEmail": "admin@allclub.com",
        "taskStatus": "COMPLETED",
        "dueDate": "2026-08-06",
        "completionRemarks": "Venue re-allocated to Studio Hall.",
        "closedAt": "2026-08-06T11:00:00",
        "approvals": [
            {"approverEmail": "admin@allclub.com", "approvalRole": "ADMIN", "approvalOrder": 1, "status": "APPROVED", "remarks": "Re-allocated."}
        ]
    },
    {
        "raisedByEmail": "karthik@allclub.com",
        "ticketType": "CREATE_EVENT_GENERAL",
        "title": "Campus Open Source Hack Sprint",
        "description": "General non-club hackathon open to all engineering departments.",
        "priority": "MEDIUM",
        "approvalStatus": "REJECTED",
        "assignedToEmail": None,
        "taskStatus": None,
        "dueDate": None,
        "completionRemarks": None,
        "approvals": [
            {"approverEmail": "admin@allclub.com", "approvalRole": "ADMIN", "approvalOrder": 1, "status": "REJECTED", "remarks": "Conflicts with semester mid-term exam schedule."}
        ]
    }
]

ASSIGNMENT_TICKET_SEED_DATA = [
    {
        "holderEmail": "rahul@allclub.com",
        "assignmentRole": "ORGANIZER",
        "referenceType": "CLUB",
        "clubName": "AI Club",
        "durationType": "INDEFINITE",
        "startsAt": "2026-01-01T00:00:00",
        "endsAt": None,
        "status": "ACTIVE",
        "grantedByEmail": "admin@allclub.com"
    },
    {
        "holderEmail": "sneha@allclub.com",
        "assignmentRole": "VOLUNTEER",
        "referenceType": "CLUB",
        "clubName": "Drama Club",
        "durationType": "DATE_RANGE",
        "startsAt": "2026-08-01T00:00:00",
        "endsAt": "2026-12-31T23:59:59",
        "status": "ACTIVE",
        "grantedByEmail": "priya@allclub.com"
    },
    {
        "holderEmail": "meena@allclub.com",
        "assignmentRole": "FACULTY_COORDINATOR",
        "referenceType": "CLUB",
        "clubName": "Science Club",
        "durationType": "INDEFINITE",
        "startsAt": "2026-02-15T00:00:00",
        "endsAt": None,
        "status": "ACTIVE",
        "grantedByEmail": "admin@allclub.com"
    },
    {
        "holderEmail": "ananya@allclub.com",
        "assignmentRole": "EVENT_ORGANIZER",
        "referenceType": "EVENT",
        "eventName": "Stagecraft Workshop",
        "durationType": "DATE_RANGE",
        "startsAt": "2026-08-15T00:00:00",
        "endsAt": "2026-08-25T23:59:59",
        "status": "ACTIVE",
        "grantedByEmail": "priya@allclub.com"
    },
    {
        "holderEmail": "vikram@allclub.com",
        "assignmentRole": "VOLUNTEER",
        "referenceType": "CLUB",
        "clubName": "Sports Club",
        "durationType": "DATE_RANGE",
        "startsAt": "2026-05-01T00:00:00",
        "endsAt": "2026-07-01T00:00:00",
        "status": "EXPIRED",
        "grantedByEmail": "arjun@allclub.com"
    },
    {
        "holderEmail": "karthik@allclub.com",
        "assignmentRole": "ORGANIZER",
        "referenceType": "CLUB",
        "clubName": "Coding Club",
        "durationType": "INDEFINITE",
        "startsAt": "2026-03-01T00:00:00",
        "endsAt": None,
        "status": "SUSPENDED",
        "grantedByEmail": "admin@allclub.com"
    },
    {
        "holderEmail": "meera@allclub.com",
        "assignmentRole": "VOLUNTEER",
        "referenceType": "CLUB",
        "clubName": "Photography Club",
        "durationType": "DATE_RANGE",
        "startsAt": "2026-04-01T00:00:00",
        "endsAt": "2026-06-01T00:00:00",
        "status": "TERMINATED",
        "grantedByEmail": "admin@allclub.com"
    }
]