export const events = [
  {
    id: 1,
    emoji: '📷',
    name: 'Photography Workshop',
    title: 'Photography Workshop',
    club: 'Photography Club',
    type: 'Workshop',
    status: 'Live',
    venue: 'Media Lab, Block C',
    startDate: '22 Jul 2026',
    endDate: '22 Jul 2026',
    startTime: '10:00 AM',
    endTime: '04:00 PM',
    description: 'A hands-on workshop covering composition, lighting and editing basics for beginners and enthusiasts.',
    schedule: [
      { time: '10:00 AM', activity: 'Registration & Welcome' },
      { time: '10:30 AM', activity: 'Basics of Composition' },
      { time: '12:00 PM', activity: 'Outdoor Photo Walk' },
      { time: '02:00 PM', activity: 'Editing Session' },
      { time: '03:30 PM', activity: 'Showcase & Wrap Up' }
    ],
    announcements: [
      { title: 'Venue Confirmed', message: 'Workshop will be held at the Media Lab, Block C.', date: '20 Jul 2026' },
      { title: 'Bring Your Own Camera', message: 'DSLR or smartphone both work fine for this session.', date: '19 Jul 2026' }
    ],
    registrations: [
      { name: 'Rahul Sharma', registerNumber: 'Y24CS001', branch: 'CSE' },
      { name: 'Ananya Iyer', registerNumber: 'Y25CS002', branch: 'CSE' },
      { name: 'Karthik Raj', registerNumber: 'Y25EC003', branch: 'ECE' }
    ],
    attendance: [
      { name: 'Rahul Sharma', registerNumber: 'Y24CS001', status: 'Present' },
      { name: 'Ananya Iyer', registerNumber: 'Y25CS002', status: 'Present' },
      { name: 'Karthik Raj', registerNumber: 'Y25EC003', status: 'Absent' }
    ]
  },
  {
    id: 2,
    emoji: '🤖',
    name: 'AI Seminar',
    title: 'AI Seminar',
    club: 'Coding Club',
    status: 'Live',
    startDate: '21 Jul 2026',
    endDate: '21 Jul 2026',
    description: 'An introductory seminar on Artificial Intelligence trends, applications and career opportunities.',
    schedule: [
      { time: '11:00 AM', activity: 'Introduction to AI' },
      { time: '11:45 AM', activity: 'Guest Talk: Dr. Ravi Kumar' },
      { time: '01:00 PM', activity: 'Q&A Session' }
    ],
    announcements: [
      { title: 'Seat Limit Reached', message: 'Registrations are now closed for this seminar.', date: '20 Jul 2026' }
    ],
    registrations: [
      { name: 'Priya Nair', registerNumber: 'Y25CS002', branch: 'CSE' },
      { name: 'Mohammed Aslam', registerNumber: 'Y25CS006', branch: 'CSE' }
    ],
    attendance: []
  },
  {
    id: 3,
    emoji: '🎵',
    name: 'Music Night',
    title: 'Music Night',
    club: 'Music Club',
    status: 'Completed',
    startDate: '19 Jul 2026',
    endDate: '19 Jul 2026',
    description: 'An evening of live performances, open mic and jam sessions by club members.',
    schedule: [
      { time: '06:00 PM', activity: 'Doors Open' },
      { time: '06:30 PM', activity: 'Open Mic' },
      { time: '08:00 PM', activity: 'Band Performances' },
      { time: '09:30 PM', activity: 'Closing Jam' }
    ],
    announcements: [
      { title: 'Thank You!', message: 'Thanks to everyone who performed and attended. Photos coming soon.', date: '19 Jul 2026' }
    ],
    registrations: [
      { name: 'Priya Nair', registerNumber: 'Y25CS002', branch: 'CSE' },
      { name: 'Sara Thomas', registerNumber: 'Y24EE007', branch: 'EEE' }
    ],
    attendance: [
      { name: 'Priya Nair', registerNumber: 'Y25CS002', status: 'Present' },
      { name: 'Sara Thomas', registerNumber: 'Y24EE007', status: 'Present' }
    ]
  },
  {
    id: 201,
    emoji: '🎸',
    name: 'Annual Campus Music Fest',
    title: 'Annual Campus Music Fest',
    club: 'Music Club',
    status: 'Live',
    startDate: '05 Aug 2026',
    endDate: '06 Aug 2026',
    description: 'Inter-college music competition featuring bands, solos, and acoustic jam sessions.',
    schedule: [
      { time: '05:00 PM', activity: 'Battle of the Bands' },
      { time: '08:00 PM', activity: 'Headliner Band Performance' }
    ],
    announcements: [
      { title: 'Registration Open', message: 'Auditions start this Friday in Auditorium Hall A.', date: '21 Jul 2026' }
    ],
    registrations: [
      { name: 'Rahul Sharma', registerNumber: 'Y24CS001', branch: 'CSE' },
      { name: 'Siddharth V', registerNumber: 'Y24ME008', branch: 'ME' }
    ],
    attendance: []
  },
  {
    id: 202,
    emoji: '🎻',
    name: 'Acoustic Night',
    title: 'Acoustic Night',
    club: 'Music Club',
    status: 'Completed',
    startDate: '12 Jun 2026',
    endDate: '12 Jun 2026',
    description: 'Unplugged acoustic music evening showcasing acoustic guitar and vocal performances.',
    schedule: [
      { time: '06:30 PM', activity: 'Acoustic Jam Session' }
    ],
    announcements: [],
    registrations: [],
    attendance: []
  },
  {
    id: 301,
    emoji: '🤖',
    name: 'AI & Machine Learning Workshop',
    title: 'AI & Machine Learning Workshop',
    club: 'AI Club',
    status: 'Live',
    startDate: '25 Jul 2026',
    endDate: '27 Jul 2026',
    description: 'Hands-on intensive workshop covering Neural Networks, PyTorch, and Deep Learning model deployment.',
    schedule: [
      { time: '09:30 AM', activity: 'Keynote & AI Trends Overview' },
      { time: '11:15 AM', activity: 'Building Convolutional Neural Nets' },
      { time: '02:30 PM', activity: 'Model Optimization & Deployment' }
    ],
    announcements: [
      { title: 'Pre-requisites Released', message: 'Please install Python 3.10 and PyTorch before attending.', date: '20 Jul 2026' }
    ],
    registrations: [
      { name: 'Kavya Singh', registerNumber: 'Y23CS009', branch: 'CSE' },
      { name: 'Rohan Verma', registerNumber: 'Y23EC010', branch: 'ECE' }
    ],
    attendance: [
      { name: 'Kavya Singh', registerNumber: 'Y23CS009', status: 'Present' },
      { name: 'Rohan Verma', registerNumber: 'Y23EC010', status: 'Present' }
    ]
  },
  {
    id: 302,
    emoji: '🚀',
    name: 'AI Hackathon 2026',
    title: 'AI Hackathon 2026',
    club: 'AI Club',
    status: 'Live',
    startDate: '15 Aug 2026',
    endDate: '16 Aug 2026',
    description: '24-hour campus hackathon building generative AI applications for real-world problems.',
    schedule: [
      { time: '09:00 AM', activity: 'Hackathon Kickoff & Problem Statements' },
      { time: '09:00 PM', activity: 'Mid-way Mentorship Checkin' },
      { time: '04:00 PM', activity: 'Final Demos & Judging' }
    ],
    announcements: [],
    registrations: [],
    attendance: []
  },
  {
    id: 401,
    emoji: '📷',
    name: 'Campus Photography Walk',
    title: 'Campus Photography Walk',
    club: 'Photography Club',
    status: 'Live',
    startDate: '02 Aug 2026',
    endDate: '02 Aug 2026',
    description: 'Golden hour outdoor photography expedition focusing on architectural and nature composition.',
    schedule: [
      { time: '06:30 AM', activity: 'Gathering at Main Gate & Lens Briefing' },
      { time: '08:00 AM', activity: 'Botanical Garden Trail Walk' },
      { time: '10:30 AM', activity: 'Photo Review & Critique Session' }
    ],
    announcements: [
      { title: 'Bring Extra SD Cards', message: 'Charge your camera batteries and format SD cards in advance.', date: '21 Jul 2026' }
    ],
    registrations: [
      { name: 'Varun K', registerNumber: 'Y25ME011', branch: 'ME' },
      { name: 'Divya P', registerNumber: 'Y25CE012', branch: 'CIVIL' }
    ],
    attendance: [
      { name: 'Varun K', registerNumber: 'Y25ME011', status: 'Present' },
      { name: 'Divya P', registerNumber: 'Y25CE012', status: 'Present' }
    ]
  },
  {
    id: 402,
    emoji: '💡',
    name: 'Portrait Lighting Masterclass',
    title: 'Portrait Lighting Masterclass',
    club: 'Photography Club',
    status: 'Completed',
    startDate: '10 Jun 2026',
    endDate: '10 Jun 2026',
    description: 'Studio lighting workshop exploring 3-point lighting setups, reflectors, and portrait retouching.',
    schedule: [
      { time: '02:00 PM', activity: 'Lighting Fundamentals & Softboxes' },
      { time: '04:00 PM', activity: 'Live Studio Model Shooting' }
    ],
    announcements: [],
    registrations: [],
    attendance: []
  }
]