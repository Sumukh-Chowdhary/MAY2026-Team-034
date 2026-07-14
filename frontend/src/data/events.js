export const events = [
  {
    id: 1,
    emoji: '📷',
    name: 'Photography Workshop',
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
      { name: 'Rahul Sharma', registerNumber: 'CB.SC.U4CSE22001', branch: 'CSE' },
      { name: 'Ananya Iyer', registerNumber: 'CB.SC.U4CSE22015', branch: 'CSE' },
      { name: 'Karthik Raj', registerNumber: 'CB.SC.U4ECE22007', branch: 'ECE' }
    ],
    attendance: [
      { name: 'Rahul Sharma', registerNumber: 'CB.SC.U4CSE22001', status: 'Present' },
      { name: 'Ananya Iyer', registerNumber: 'CB.SC.U4CSE22015', status: 'Present' },
      { name: 'Karthik Raj', registerNumber: 'CB.SC.U4ECE22007', status: 'Absent' }
    ]
  },
  {
    id: 2,
    emoji: '🤖',
    name: 'AI Seminar',
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
      { name: 'Priya Nair', registerNumber: 'CB.SC.U4CSE22002', branch: 'CSE' },
      { name: 'Mohammed Aslam', registerNumber: 'CB.SC.U4CSE22030', branch: 'CSE' }
    ],
    attendance: []
  },
  {
    id: 3,
    emoji: '🎵',
    name: 'Music Night',
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
      { name: 'Priya Nair', registerNumber: 'CB.SC.U4CSE22002', branch: 'CSE' },
      { name: 'Sara Thomas', registerNumber: 'CB.SC.U4EEE22011', branch: 'EEE' }
    ],
    attendance: [
      { name: 'Priya Nair', registerNumber: 'CB.SC.U4CSE22002', status: 'Present' },
      { name: 'Sara Thomas', registerNumber: 'CB.SC.U4EEE22011', status: 'Present' }
    ]
  }
]