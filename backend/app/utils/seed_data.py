"""
Comprehensive AllClub Seed Data Definition File
Contains deterministic seed data for:
- 9 Departments
- 2 Admins, 1 Principal, 20 Faculty, 100 Students
- 20 Clubs
- 10 Venues
"""

import random

random.seed(42)

DEPARTMENTS_DATA = [
    {"name": "Administration", "code": "ADM"},
    {"name": "Computer Science & Engineering", "code": "CSE"},
    {"name": "Electronics & Communication", "code": "ECE"},
    {"name": "Information Technology", "code": "IT"},
    {"name": "Mechanical Engineering", "code": "ME"},
    {"name": "Civil Engineering", "code": "CE"},
    {"name": "Electrical & Electronics", "code": "EEE"},
    {"name": "Data Science & AI", "code": "DS"},
    {"name": "Management Studies", "code": "MBA"}
]

ADMIN_DATA_LIST = [
    {
        "email": "admin@allclub.com",
        "password": "admin123",
        "roll_no": "ADM001",
        "full_name": "Admin User",
        "phone_number": "+91 90000 00001",
        "department": "ADM",
        "bio": "Platform administrator managing all campus clubs, events, and approvals."
    },
    {
        "email": "admin2@allclub.com",
        "password": "admin123",
        "roll_no": "ADM002",
        "full_name": "System Administrator",
        "phone_number": "+91 90000 00002",
        "department": "ADM",
        "bio": "Secondary platform administrator overseeing technical operations and system audit."
    }
]

PRINCIPAL_DATA = {
    "email": "principal@allclub.com",
    "password": "principal123",
    "employee_id": "PRIN001",
    "full_name": "Dr. K. S. Murthy (Principal)",
    "phone_number": "+91 90000 00000",
    "department": "ADM",
    "designation": "PRINCIPAL",
    "bio": "Principal of the institution overseeing overall academic, institutional, and extracurricular affairs."
}

FACULTY_NAMES_AND_DEPTS = [
    ("Dr. Meena Rao", "CSE", "Associate Professor", "Research in machine learning and distributed systems."),
    ("Dr. Arjun Nair", "ECE", "Assistant Professor", "Specialist in embedded systems, IoT, and robotics."),
    ("Dr. Priya Iyer", "CSE", "Professor", "HOD of Computer Science. AI and Data Science researcher."),
    ("Dr. Rajesh Sharma", "IT", "Associate Professor", "Cloud computing and cybersecurity academic lead."),
    ("Dr. Sunita Verma", "ME", "Professor", "Fluid dynamics and thermal engineering specialist."),
    ("Dr. Anil Kulkarni", "CE", "Associate Professor", "Structural engineering and green building consultant."),
    ("Dr. Kavita Deshmukh", "EEE", "Assistant Professor", "Power systems and renewable energy researcher."),
    ("Dr. Vikramaditya Sen", "DS", "Professor", "Head of Data Science Initiative. Neural network pioneer."),
    ("Dr. Ramesh Babu", "MBA", "Associate Professor", "Dean of Management Studies. Startup mentor."),
    ("Dr. Swati Bhattacharya", "CSE", "Assistant Professor", "Human-computer interaction and web technologies."),
    ("Dr. Alok Gupta", "ECE", "Professor", "VLSI design and signal processing expert."),
    ("Dr. Pooja Saxena", "IT", "Assistant Professor", "Software engineering and agile dev practices."),
    ("Dr. Harish Prasad", "ME", "Associate Professor", "Mechatronics and industrial automation head."),
    ("Dr. Geeta Krishnan", "CE", "Assistant Professor", "Environmental engineering and waste management."),
    ("Dr. Anand Joshi", "EEE", "Professor", "Control systems and smart grid technologies."),
    ("Dr. Deepa Nambiar", "DS", "Associate Professor", "Natural language processing and big data analytics."),
    ("Dr. Sanjay Roy", "MBA", "Assistant Professor", "Financial markets and corporate finance expert."),
    ("Dr. Radhika Chawla", "CSE", "Assistant Professor", "Algorithm design and competitive programming lead."),
    ("Dr. Manoj Pandey", "ME", "Assistant Professor", "CAD/CAM and 3D printing technologies."),
    ("Dr. Archana Hegde", "IT", "Associate Professor", "Network security and cryptography expert.")
]

FACULTY_DATA_LIST = [PRINCIPAL_DATA]
for idx, (fname, dept, desig, fbio) in enumerate(FACULTY_NAMES_AND_DEPTS, start=1):
    f_email = fname.split()[-1].lower() + "@allclub.com"
    if idx == 1: f_email = "meena@allclub.com"
    elif idx == 2: f_email = "arjun@allclub.com"
    elif idx == 3: f_email = "priya@allclub.com"

    FACULTY_DATA_LIST.append({
        "email": f_email,
        "password": "faculty123",
        "employee_id": f"FAC{idx:03d}",
        "full_name": fname,
        "phone_number": f"+91 98765 {idx:05d}",
        "department": dept,
        "designation": desig,
        "bio": fbio
    })

FIRST_NAMES = [
    "Rahul", "Ananya", "Vikram", "Sneha", "Karthik", "Meera", "Rohan", "Divya",
    "Amit", "Pooja", "Siddharth", "Neha", "Aditya", "Kavya", "Suresh", "Ritu",
    "Varun", "Priya", "Nikhil", "Shreya", "Abhishek", "Tanvi", "Gaurav", "Isha",
    "Deepak", "Rhea", "Manish", "Aarti", "Tarun", "Krutika", "Akash", "Bhavna",
    "Karan", "Simran", "Yash", "Pallavi", "Vivek", "Nisha", "Harsh", "Swati",
    "Sameer", "Preeti", "Sanjay", "Ankita", "Pranav", "Juhi", "Mayank", "Sonam",
    "Rajesh", "Poonam"
]

LAST_NAMES = [
    "Sharma", "Gupta", "Singh", "Nair", "Rao", "Das", "Verma", "Kapoor",
    "Patel", "Joshi", "Menon", "Reddy", "Bose", "Kulkarni", "Kumar", "Agarwal",
    "Mishra", "Deshmukh", "Chawla", "Bhattacharya", "Roy", "Hegde", "Pandey", "Saxena",
    "Prasad", "Krishnan", "Joshi", "Nambiar", "Sen", "Babu"
]

from app.utils.registration_id import generate_registration_id

DEPTS_LIST = ["CSE", "ECE", "IT", "ME", "CE", "EEE", "DS", "MBA"]
YEARS_LIST = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
YEAR_TO_BATCH = {
    "1st Year": 2026,
    "2nd Year": 2025,
    "3rd Year": 2024,
    "4th Year": 2023
}

STUDENT_DATA_LIST = [
    {
        "email": "rahul@allclub.com",
        "password": "student123",
        "roll_no": generate_registration_id(2024, "CSE", 1), # Y24CS001
        "full_name": "Rahul Sharma",
        "phone_number": "+91 90000 00003",
        "year_of_study": "3rd Year",
        "department": "CSE",
        "bio": "Lead developer and tech enthusiast passionate about web dev and AI."
    },
    {
        "email": "ananya@allclub.com",
        "password": "student123",
        "roll_no": generate_registration_id(2025, "CSE", 2), # Y25CS002
        "full_name": "Ananya Gupta",
        "phone_number": "+91 90000 00006",
        "year_of_study": "2nd Year",
        "department": "CSE",
        "bio": "UI/UX design enthusiast and student organizer."
    },
    {
        "email": "vikram@allclub.com",
        "password": "student123",
        "roll_no": generate_registration_id(2023, "ECE", 3), # Y23EC003
        "full_name": "Vikram Singh",
        "phone_number": "+91 90000 00007",
        "year_of_study": "4th Year",
        "department": "ECE",
        "bio": "Electronics enthusiast and robotics lead."
    },
    {
        "email": "sneha@allclub.com",
        "password": "student123",
        "roll_no": generate_registration_id(2026, "CSE", 4), # Y26CS004
        "full_name": "Sneha Nair",
        "phone_number": "+91 90000 00008",
        "year_of_study": "1st Year",
        "department": "CSE",
        "bio": "Interested in theatre, public speaking, and open-source contribution."
    },
    {
        "email": "karthik@allclub.com",
        "password": "student123",
        "roll_no": generate_registration_id(2024, "ECE", 5), # Y24EC005
        "full_name": "Karthik Rao",
        "phone_number": "+91 90000 00009",
        "year_of_study": "3rd Year",
        "department": "ECE",
        "bio": "Passionate about microcontrollers and embedded firmware."
    },
    {
        "email": "meera@allclub.com",
        "password": "student123",
        "roll_no": generate_registration_id(2025, "CSE", 6), # Y25CS006
        "full_name": "Meera Das",
        "phone_number": "+91 90000 00010",
        "year_of_study": "2nd Year",
        "department": "CSE",
        "bio": "Aspiring software engineer and photography hobbyist."
    }
]

LEGACY_EXPLICIT_STUDENT_LIST = [
    {
        "email": "legacy_rahul@allclub.com",
        "password": "student123",
        "roll_no": "Y22CS001",
        "full_name": "Rahul Verma (Alumni)",
        "phone_number": "+91 98765 43210",
        "year_of_study": "Graduated",
        "department": "CSE",
        "account_status": "LEGACY",
        "bio": "Former Lead Developer & AI Club Vice President (Batch 2022-2026). Currently Software Engineer at Google."
    },
    {
        "email": "legacy_ananya@allclub.com",
        "password": "student123",
        "roll_no": "Y22EC004",
        "full_name": "Ananya Sharma (Alumni)",
        "phone_number": "+91 98765 43211",
        "year_of_study": "Graduated",
        "department": "ECE",
        "account_status": "LEGACY",
        "bio": "Former Drama Club Organizer & Event Lead (Batch 2022-2026). Currently Hardware Design Engineer at Intel."
    },
    {
        "email": "legacy_vikram@allclub.com",
        "password": "student123",
        "roll_no": "Y21ME002",
        "full_name": "Vikram Patel (Alumni)",
        "phone_number": "+91 98765 43212",
        "year_of_study": "Graduated",
        "department": "ME",
        "account_status": "LEGACY",
        "bio": "Former Robotics Club Volunteer & Student Lead (Batch 2021-2025). Currently Systems Engineer at Tesla."
    }
]

STUDENT_DATA_LIST.extend(LEGACY_EXPLICIT_STUDENT_LIST)

# Generate remaining 91 students deterministically
for idx in range(7, 98):
    fn = FIRST_NAMES[(idx * 3) % len(FIRST_NAMES)]
    ln = LAST_NAMES[(idx * 7) % len(LAST_NAMES)]
    full_n = f"{fn} {ln}"
    s_email = f"student{idx}@allclub.com"
    dept = DEPTS_LIST[idx % len(DEPTS_LIST)]
    is_legacy = (85 <= idx <= 97)
    yr = "Graduated" if is_legacy else YEARS_LIST[idx % len(YEARS_LIST)]
    batch_yr = 2021 if is_legacy else YEAR_TO_BATCH.get(yr, 2026)
    status = "LEGACY" if is_legacy else "ACTIVE"
    
    STUDENT_DATA_LIST.append({
        "email": s_email,
        "password": "student123",
        "roll_no": generate_registration_id(batch_yr, dept, idx),
        "full_name": full_n,
        "phone_number": f"+91 91234 {idx:05d}",
        "year_of_study": yr,
        "department": dept,
        "account_status": status,
        "bio": f"{'Alumni / Graduated' if is_legacy else yr} {dept} student active in campus events and technical societies."
    })

CLUB_DATA_LIST = [
    {
        "name": "AI Club",
        "category": "Technology",
        "description": "Fostering research, workshops, and hackathons in Artificial Intelligence, Deep Learning, and Computer Vision.",
        "logo": "psychology",
        "faculty_emp_id": "FAC001", # Dr. Meena Rao
        "organizer_roll_no": STUDENT_DATA_LIST[0]["roll_no"] # Rahul Sharma
    },
    {
        "name": "Coding Club",
        "category": "Technical",
        "description": "Promoting algorithmic thinking, competitive programming, and open-source software development.",
        "logo": "terminal",
        "faculty_emp_id": "FAC001",
        "organizer_roll_no": STUDENT_DATA_LIST[0]["roll_no"]
    },
    {
        "name": "Robotics Club",
        "category": "Technical",
        "description": "Designing autonomous robots, IoT hardware, and competing in national tech expos.",
        "logo": "smart_toy",
        "faculty_emp_id": "FAC002", # Dr. Arjun Nair
        "organizer_roll_no": STUDENT_DATA_LIST[2]["roll_no"] # Vikram Singh
    },
    {
        "name": "Photography Club",
        "category": "Creative",
        "description": "Capturing campus life, hosting photo walks, and conducting digital editing masterclasses.",
        "logo": "photo_camera",
        "faculty_emp_id": "FAC001",
        "organizer_roll_no": STUDENT_DATA_LIST[5]["roll_no"] # Meera Das
    },
    {
        "name": "Drama Club",
        "category": "Cultural",
        "description": "Theatrical performances, stagecraft, street plays, and monologue competitions.",
        "logo": "theater_comedy",
        "faculty_emp_id": "FAC003", # Dr. Priya Iyer
        "organizer_roll_no": STUDENT_DATA_LIST[3]["roll_no"] # Sneha Nair
    },
    {
        "name": "Music Club",
        "category": "Arts",
        "description": "Acoustic jam sessions, classical recitals, and campus band competitions.",
        "logo": "music_note",
        "faculty_emp_id": "FAC003",
        "organizer_roll_no": STUDENT_DATA_LIST[6]["roll_no"]
    },
    {
        "name": "Debate Club",
        "category": "Academic",
        "description": "Parliamentary debates, extempore competitions, and Model United Nations (MUN) training.",
        "logo": "forum",
        "faculty_emp_id": "FAC004",
        "organizer_roll_no": STUDENT_DATA_LIST[7]["roll_no"]
    },
    {
        "name": "Literary Club",
        "category": "Academic",
        "description": "Creative writing, poetry slams, book discussions, and campus newsletter editorial.",
        "logo": "menu_book",
        "faculty_emp_id": "FAC004",
        "organizer_roll_no": STUDENT_DATA_LIST[8]["roll_no"]
    },
    {
        "name": "Entrepreneurship Club",
        "category": "Management",
        "description": "Ideation pitch fests, startup incubation guidance, and business model development.",
        "logo": "rocket_launch",
        "faculty_emp_id": "FAC009", # Dr. Ramesh Babu
        "organizer_roll_no": STUDENT_DATA_LIST[9]["roll_no"]
    },
    {
        "name": "Cyber Security Club",
        "category": "Technical",
        "description": "Capture The Flag (CTF) challenges, ethical hacking, and network defense security.",
        "logo": "shield",
        "faculty_emp_id": "FAC004",
        "organizer_roll_no": STUDENT_DATA_LIST[10]["roll_no"]
    },
    {
        "name": "Data Science Club",
        "category": "Technology",
        "description": "Data analytics, Kaggle competitions, machine learning models, and visualization dashboards.",
        "logo": "analytics",
        "faculty_emp_id": "FAC008", # Dr. Vikramaditya Sen
        "organizer_roll_no": STUDENT_DATA_LIST[11]["roll_no"]
    },
    {
        "name": "Astronomy Club",
        "category": "Science",
        "description": "Night sky observation, telescope workshops, and astrophysics discussions.",
        "logo": "auto_awesome",
        "faculty_emp_id": "FAC002",
        "organizer_roll_no": STUDENT_DATA_LIST[12]["roll_no"]
    },
    {
        "name": "Mechanical Innovation Club",
        "category": "Technical",
        "description": "CAD design competitions, 3D printing prototyping, and mechatronic systems.",
        "logo": "precision_manufacturing",
        "faculty_emp_id": "FAC005", # Dr. Sunita Verma
        "organizer_roll_no": STUDENT_DATA_LIST[13]["roll_no"]
    },
    {
        "name": "Eco Club",
        "category": "Social",
        "description": "Tree plantation drives, campus sustainability projects, and environmental awareness.",
        "logo": "eco",
        "faculty_emp_id": "FAC006", # Dr. Anil Kulkarni
        "organizer_roll_no": STUDENT_DATA_LIST[14]["roll_no"]
    },
    {
        "name": "Dance Club",
        "category": "Cultural",
        "description": "Choreography workshops, inter-college dance face-offs, and showcase galas.",
        "logo": "directions_run",
        "faculty_emp_id": "FAC007",
        "organizer_roll_no": STUDENT_DATA_LIST[15]["roll_no"]
    },
    {
        "name": "Film Club",
        "category": "Creative",
        "description": "Short film screenings, video editing masterclasses, and campus cinema festivals.",
        "logo": "movie",
        "faculty_emp_id": "FAC010",
        "organizer_roll_no": STUDENT_DATA_LIST[16]["roll_no"]
    },
    {
        "name": "Finance Club",
        "category": "Management",
        "description": "Stock market simulation games, financial literacy sessions, and investment analysis.",
        "logo": "account_balance",
        "faculty_emp_id": "FAC017", # Dr. Sanjay Roy
        "organizer_roll_no": STUDENT_DATA_LIST[17]["roll_no"]
    },
    {
        "name": "Gaming Club",
        "category": "Entertainment",
        "description": "LAN gaming tournaments, esports leagues, and game development sprints.",
        "logo": "sports_esports",
        "faculty_emp_id": "FAC012",
        "organizer_roll_no": STUDENT_DATA_LIST[18]["roll_no"]
    },
    {
        "name": "Design Club",
        "category": "Creative",
        "description": "UI/UX design sprints, poster artwork design, and digital illustration workshops.",
        "logo": "palette",
        "faculty_emp_id": "FAC010",
        "organizer_roll_no": STUDENT_DATA_LIST[19]["roll_no"]
    },
    {
        "name": "Mathematics Club",
        "category": "Academic",
        "description": "Math Olympiad training, logic puzzles, and quantitative problem solving.",
        "logo": "functions",
        "faculty_emp_id": "FAC018",
        "organizer_roll_no": STUDENT_DATA_LIST[20]["roll_no"]
    }
]

VENUE_DATA_LIST = [
    {
        "name": "Main Auditorium",
        "location": "Block A, 2nd Floor",
        "type": "Auditorium",
        "capacity": 300,
        "availabilityStatus": "AVAILABLE"
    },
    {
        "name": "Innovation Lab",
        "location": "Block C, Lab 3",
        "type": "Lab",
        "capacity": 80,
        "availabilityStatus": "AVAILABLE"
    },
    {
        "name": "Open Air Ground",
        "location": "North Campus",
        "type": "Ground",
        "capacity": 500,
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
        "availabilityStatus": "AVAILABLE"
    },
    {
        "name": "Robotics Lab",
        "location": "Block C, Ground Floor",
        "type": "Lab",
        "capacity": 50,
        "availabilityStatus": "AVAILABLE"
    },
    {
        "name": "Sports Complex Ground",
        "location": "South Campus",
        "type": "Ground",
        "capacity": 800,
        "availabilityStatus": "AVAILABLE"
    },
    {
        "name": "Computer Center Lab 1",
        "location": "Block B, Floor 2",
        "type": "Lab",
        "capacity": 100,
        "availabilityStatus": "AVAILABLE"
    },
    {
        "name": "Open Air Theatre",
        "location": "Central Campus",
        "type": "Auditorium",
        "capacity": 350,
        "availabilityStatus": "AVAILABLE"
    }
]