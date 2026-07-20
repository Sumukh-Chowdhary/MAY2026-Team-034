<script setup>
import { ref } from 'vue'
import FacultyLayout from '@/layouts/FacultyLayout.vue'

// Faculty assigned roles (Clubs & Events)
const facultyRoles = ref([
  {
    id: 1,
    roleTitle: 'Faculty Coordinator',
    clubName: 'AI Club',
    type: 'Club',
    emoji: '🤖',
    totalMembers: 48,
    coCoordinators: ['Dr. Ramesh Kumar', 'Dr. Meenakshi S'],
    description: 'Directing club operations, evaluating event proposals, and overseeing student organizer roles.',
    assignedStudents: [
      { id: 101, name: 'Rahul Sharma', roll: 'CS21B001', branch: 'CSE', email: 'rahul.s@campus.edu', role: 'Club Organizer', status: 'Active', joinDate: '10 Aug 2024', phone: '+91 98765 43210', eventsAttended: 12 },
      { id: 102, name: 'Priya Nair', roll: 'CS22B005', branch: 'CSE', email: 'priya.n@campus.edu', role: 'Event Volunteer', status: 'Active', joinDate: '15 Jan 2025', phone: '+91 98765 12345', eventsAttended: 8 },
      { id: 103, name: 'Arjun Mehta', roll: 'EC22B022', branch: 'ECE', email: 'arjun.m@campus.edu', role: 'Member', status: 'Active', joinDate: '01 Nov 2025', phone: '+91 98765 67890', eventsAttended: 4 }
    ],
    alumni: [
      { name: 'Vikram Seth', roll: 'CS18B011', branch: 'CSE', passoutYear: '2022', formerRole: 'Lead Organizer' },
      { name: 'Siddharth R', roll: 'EE19B040', branch: 'EEE', passoutYear: '2023', formerRole: 'Tech Volunteer' }
    ],
    events: [
      {
        id: 301,
        title: 'AI & Machine Learning Workshop',
        club: 'AI Club',
        status: 'Active',
        startDate: '25 Jul 2026',
        endDate: '27 Jul 2026',
        description: 'Hands-on intensive workshop covering Neural Networks, PyTorch, and Deep Learning model deployment.',
        schedule: [
          { time: '09:30 AM', activity: 'Keynote & AI Trends Overview' },
          { time: '11:15 AM', activity: 'Building Convolutional Neural Nets' },
          { time: '02:30 PM', activity: 'Model Optimization & Deployment' }
        ],
        announcements: [
          { id: 1, title: 'Pre-requisites Released', date: '20 Jul 2026', message: 'Please install Python 3.10 and PyTorch before attending.', target: 'All' }
        ],
        registrations: [
          { name: 'Kavya Singh', registerNumber: '21B0012', branch: 'CSE' },
          { name: 'Rohan Verma', registerNumber: '21B0045', branch: 'ECE' }
        ],
        attendance: [
          { name: 'Kavya Singh', registerNumber: '21B0012', present: true },
          { name: 'Rohan Verma', registerNumber: '21B0045', present: true }
        ]
      },
      {
        id: 302,
        title: 'AI Hackathon 2026',
        club: 'AI Club',
        status: 'Active',
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
      }
    ]
  },
  {
    id: 2,
    roleTitle: 'Faculty Advisor',
    clubName: 'Photography Club',
    type: 'Club',
    emoji: '📷',
    totalMembers: 27,
    coCoordinators: ['Prof. Vikram Adve'],
    description: 'Fostering visual storytelling, organizing photo expeditions, masterclasses, and annual photo exhibitions.',
    assignedStudents: [
      { id: 201, name: 'Ananya Roy', roll: 'EE21B014', branch: 'EEE', email: 'ananya.r@campus.edu', role: 'Club Organizer', status: 'Active', joinDate: '05 Sep 2024', phone: '+91 91234 56789', eventsAttended: 15 },
      { id: 202, name: 'Siddharth V', roll: 'ME21B033', branch: 'ME', email: 'siddharth.v@campus.edu', role: 'Event Volunteer', status: 'Active', joinDate: '12 Jan 2025', phone: '+91 91234 98765', eventsAttended: 9 },
      { id: 203, name: 'Rohan Mehra', roll: 'CS22B088', branch: 'CSE', email: 'rohan.m@campus.edu', role: 'Member', status: 'Active', joinDate: '20 Oct 2025', phone: '+91 91234 11223', eventsAttended: 3 }
    ],
    alumni: [
      { name: 'Kavya S', roll: 'MM19B002', branch: 'MSE', passoutYear: '2023', formerRole: 'President & Head Photographer' }
    ],
    events: [
      {
        id: 401,
        title: 'Campus Photography Walk',
        club: 'Photography Club',
        status: 'Active',
        startDate: '02 Aug 2026',
        endDate: '02 Aug 2026',
        description: 'Golden hour outdoor photography expedition focusing on architectural and nature composition.',
        schedule: [
          { time: '06:30 AM', activity: 'Gathering at Main Gate & Lens Briefing' },
          { time: '08:00 AM', activity: 'Botanical Garden Trail Walk' },
          { time: '10:30 AM', activity: 'Photo Review & Critique Session' }
        ],
        announcements: [
          { id: 1, title: 'Bring Extra SD Cards', date: '21 Jul 2026', message: 'Charge your camera batteries and format SD cards in advance.', target: 'Students' }
        ],
        registrations: [
          { name: 'Varun K', registerNumber: '22B0011', branch: 'ME' },
          { name: 'Divya P', registerNumber: '22B0077', branch: 'CIVIL' }
        ],
        attendance: [
          { name: 'Varun K', registerNumber: '22B0011', present: true },
          { name: 'Divya P', registerNumber: '22B0077', present: true }
        ]
      },
      {
        id: 402,
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
  }
])

// Incoming Student Requests Panel Data
const incomingRequests = ref([
  { id: 1, studentName: 'Rohan Gupta', roll: 'CS23B012', type: 'Club Join Request', clubName: 'AI Club', details: 'Wants to join AI Club as active member' },
  { id: 2, studentName: 'Aditi Sharma', roll: 'EE22B009', type: 'Event Creation Proposal', clubName: 'AI Club', details: 'Proposal for Robotics & Hardware Expo' },
  { id: 3, studentName: 'Karthik V', roll: 'ME23B045', type: 'Volunteer Application', clubName: 'Photography Club', details: 'Applying for Photowalk logistics volunteer' }
])

// Active Navigation States
const activeRoleView = ref(null)
const activeClubTab = ref('details') // 'details', 'members', 'events', 'alumni'

// Modals State
const showUserProfileModal = ref(false)
const selectedUserProfile = ref(null)

const showEventDetailsModal = ref(false)
const selectedEventDetails = ref(null)
const activeEventTabInModal = ref('schedule') // 'schedule', 'announcements', 'registrations', 'attendance'

const showAssignRoleModal = ref(false)
const selectedStudentForAssign = ref(null)
const assignRoleInput = ref('')
const assignRoleDescInput = ref('')

const showRejectModal = ref(false)
const selectedRequestForReject = ref(null)
const rejectionReason = ref('')

// Form state inside Event Details modal
const showAddScheduleModal = ref(false)
const newScheduleTime = ref('')
const newScheduleActivity = ref('')

const showAddAnnouncementModal = ref(false)
const newAnnouncementTitle = ref('')
const newAnnouncementMessage = ref('')
const newAnnouncementTarget = ref('All')

function openFacultyDashboard(role) {
  activeRoleView.value = JSON.parse(JSON.stringify(role))
  activeClubTab.value = 'details'
}

function closeDashboard() {
  activeRoleView.value = null
}

// User Profile View Trigger
function openUserProfile(student) {
  selectedUserProfile.value = student
  showUserProfileModal.value = true
}

// Event Details Trigger
function openEventDetails(event) {
  selectedEventDetails.value = JSON.parse(JSON.stringify(event))
  activeEventTabInModal.value = 'schedule'
  showEventDetailsModal.value = true
}

// Assign Role (Faculty Only)
function triggerAssignRole(student) {
  selectedStudentForAssign.value = student
  assignRoleInput.value = ''
  assignRoleDescInput.value = ''
  showAssignRoleModal.value = true
}

function confirmAssignRole() {
  if (!assignRoleInput.value.trim()) return alert('Please enter role title.')
  selectedStudentForAssign.value.role = assignRoleInput.value.trim()
  alert(`Successfully assigned role "${assignRoleInput.value}" to ${selectedStudentForAssign.value.name}!`)
  showAssignRoleModal.value = false
}

// Remove Role (Faculty Only)
function handleRemoveRole(student) {
  if (confirm(`Are you sure you want to revoke the role from ${student.name}?`)) {
    student.role = 'Member'
  }
}

// Add Agenda to Event
function addScheduleItem() {
  if (!newScheduleActivity.value.trim()) return
  selectedEventDetails.value.schedule.push({
    time: newScheduleTime.value || '10:00 AM',
    activity: newScheduleActivity.value
  })
  showAddScheduleModal.value = false
  newScheduleTime.value = ''
  newScheduleActivity.value = ''
}

// Add Announcement to Event
function addAnnouncementItem() {
  if (!newAnnouncementTitle.value.trim()) return
  selectedEventDetails.value.announcements.unshift({
    id: Date.now(),
    title: newAnnouncementTitle.value,
    date: new Date().toLocaleDateString(),
    message: newAnnouncementMessage.value,
    target: newAnnouncementTarget.value
  })
  alert(`Announcement broadcasted to ${newAnnouncementTarget.value}!`)
  showAddAnnouncementModal.value = false
  newAnnouncementTitle.value = ''
  newAnnouncementMessage.value = ''
}

// Post Attendance for Event
function postAttendanceInModal() {
  const count = selectedEventDetails.value.attendance.filter(a => a.present).length
  const total = selectedEventDetails.value.attendance.length
  alert(`Attendance updated: ${count}/${total} Present.`)
}

// Request Approvals
function approveRequest(reqId) {
  incomingRequests.value = incomingRequests.value.filter(r => r.id !== reqId)
  alert('Request approved successfully!')
}

function triggerRejectRequest(req) {
  selectedRequestForReject.value = req
  rejectionReason.value = ''
  showRejectModal.value = true
}

function confirmRejectRequest() {
  if (!rejectionReason.value.trim()) return alert('Please enter rejection reason.')
  incomingRequests.value = incomingRequests.value.filter(r => r.id !== selectedRequestForReject.value.id)
  alert(`Request rejected. Reason sent to student: "${rejectionReason.value}"`)
  showRejectModal.value = false
}
</script>

<template>
  <FacultyLayout>
    <section class="roles-page">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h2>My Roles</h2>
          <p>Supervise club coordinators, manage student roles, and review incoming requests.</p>
        </div>
      </div>

      <!-- Main Roles View -->
      <div v-if="!activeRoleView">
        <!-- Managed Roles Grid -->
        <h4 class="fw-bold mb-3 text-dark">Assigned Roles</h4>
        <div class="row g-4 mb-5">
          <div v-for="role in facultyRoles" :key="role.id" class="col-12 col-md-6">
            <div class="role-card">
              <div class="role-card-header">
                <div class="role-icon">{{ role.emoji }}</div>
                <div>
                  <span class="role-badge">{{ role.roleTitle }}</span>
                  <h5 class="role-title">{{ role.clubName }}</h5>
                  <span class="text-secondary text-sm">{{ role.totalMembers }} Enrolled Members</span>
                </div>
              </div>

              <p class="role-description">{{ role.description }}</p>

              <div class="role-card-footer">
                <span class="text-secondary font-semibold text-sm">Role: {{ role.roleTitle }}</span>
                <button class="manage-btn" @click="openFacultyDashboard(role)">
                  View Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Incoming Student Requests Review Queue -->
        <div class="card p-4 shadow-sm border-0 rounded-4">
          <h4 class="fw-bold mb-3">Incoming Student Requests</h4>
          <p class="text-secondary text-sm mb-4">Review club join applications, event proposals, and volunteer requests.</p>

          <div v-if="incomingRequests.length === 0" class="text-center py-4 text-secondary">
            No pending incoming requests.
          </div>

          <div v-else class="row g-3">
            <div v-for="req in incomingRequests" :key="req.id" class="col-12 col-md-4">
              <div class="p-3 border rounded-3 bg-white shadow-sm d-flex flex-column h-100">
                <span class="badge bg-primary-subtle text-primary border mb-2 align-self-start">{{ req.type }}</span>
                <h6 class="fw-bold m-0">{{ req.studentName }}</h6>
                <small class="text-secondary">{{ req.roll }} · {{ req.clubName }}</small>
                <p class="text-sm mt-2 text-dark flex-grow-1">{{ req.details }}</p>
                <div class="d-flex gap-2 mt-3">
                  <button class="btn btn-sm btn-success flex-fill" @click="approveRequest(req.id)">Approve</button>
                  <button class="btn btn-sm btn-outline-danger flex-fill" @click="triggerRejectRequest(req)">Reject</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- UNLOCKED FACULTY DASHBOARD VIEW                                      -->
      <!-- ==================================================================== -->
      <div v-if="activeRoleView" class="unlocked-dashboard">
        <!-- Banner -->
        <div class="dashboard-banner mb-4">
          <div class="d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-3">
              <button class="back-btn" @click="closeDashboard">← Back to Roles</button>
              <div class="banner-emoji">{{ activeRoleView.emoji }}</div>
              <div>
                <h3 class="m-0 text-dark font-bold">{{ activeRoleView.clubName }}</h3>
                <span class="badge bg-success px-3 py-1 mt-1">{{ activeRoleView.roleTitle }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Clean Navigation Tabs -->
        <div class="detail-tabs mb-4">
          <button class="tab-option" :class="{ active: activeClubTab === 'details' }" @click="activeClubTab = 'details'">📌 Details</button>
          <button class="tab-option" :class="{ active: activeClubTab === 'members' }" @click="activeClubTab = 'members'">👥 Members</button>
          <button class="tab-option" :class="{ active: activeClubTab === 'events' }" @click="activeClubTab = 'events'">📅 Events</button>
          <button class="tab-option" :class="{ active: activeClubTab === 'alumni' }" @click="activeClubTab = 'alumni'">🎓 Alumni</button>
        </div>

        <!-- Tab 1: Details -->
        <div v-if="activeClubTab === 'details'" class="card p-4 shadow-sm border-0 rounded-4">
          <h5 class="fw-bold mb-3">Club Details</h5>
          <div class="row g-3">
            <div class="col-md-6">
              <div class="info-box">
                <label>Co-Faculty Coordinators / Advisors</label>
                <p>{{ activeRoleView.coCoordinators.join(', ') }}</p>
              </div>
            </div>
            <div class="col-md-6">
              <div class="info-box">
                <label>Total Registered Members</label>
                <p>{{ activeRoleView.totalMembers }} Members</p>
              </div>
            </div>
            <div class="col-12">
              <div class="info-box">
                <label>Description</label>
                <p>{{ activeRoleView.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 2: Members & User Profiles -->
        <div v-if="activeClubTab === 'members'" class="card p-4 shadow-sm border-0 rounded-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h5 class="fw-bold m-0">Student Members</h5>
              <span class="text-secondary text-sm">Click on any member's name or View button to open full student profile details.</span>
            </div>
          </div>

          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>Student Name</th>
                <th>Roll Number</th>
                <th>Branch</th>
                <th>Assigned Role</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="st in activeRoleView.assignedStudents" :key="st.id">
                <td>
                  <button class="btn btn-link text-decoration-none fw-semibold text-primary p-0" @click="openUserProfile(st)">
                    👤 {{ st.name }}
                  </button>
                </td>
                <td>{{ st.roll }}</td>
                <td>{{ st.branch }}</td>
                <td>
                  <span class="badge bg-primary-subtle text-primary border px-2 py-1">{{ st.role }}</span>
                </td>
                <td class="text-end">
                  <button class="btn btn-sm btn-light border me-2" @click="openUserProfile(st)">
                    View Profile
                  </button>
                  <button class="btn btn-sm btn-outline-success me-2" @click="triggerAssignRole(st)">
                    Assign Role
                  </button>
                  <button v-if="st.role !== 'Member'" class="btn btn-sm btn-outline-danger" @click="handleRemoveRole(st)">
                    Remove
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Tab 3: Events -->
        <div v-if="activeClubTab === 'events'" class="card p-4 shadow-sm border-0 rounded-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h5 class="fw-bold m-0">Club Events</h5>
              <span class="text-secondary text-sm">Click on any event card to view full event schedule, announcements, registrations, and attendance.</span>
            </div>
          </div>

          <div class="row g-3">
            <div v-for="ev in activeRoleView.events" :key="ev.id" class="col-md-6">
              <div class="event-card-item p-3 border rounded-3 bg-white shadow-sm" @click="openEventDetails(ev)">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h6 class="m-0 fw-bold text-primary">{{ ev.title }}</h6>
                  <span class="badge" :class="ev.status === 'Active' ? 'bg-success' : 'bg-secondary'">{{ ev.status }}</span>
                </div>
                <p class="text-sm text-secondary mb-2 line-clamp-2">{{ ev.description }}</p>
                <div class="d-flex justify-content-between align-items-center pt-2 border-top">
                  <small class="text-muted">🗓️ {{ ev.startDate }}</small>
                  <button class="btn btn-sm btn-outline-primary py-0 px-2">View Event →</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 4: Alumni Archives -->
        <div v-if="activeClubTab === 'alumni'" class="card p-4 shadow-sm border-0 rounded-4">
          <h5 class="fw-bold mb-2">Alumni Records</h5>
          <p class="text-secondary text-sm mb-4">Maintains historical records of former club members and organizers.</p>

          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>Alumni Name</th>
                <th>Roll No</th>
                <th>Branch</th>
                <th>Passout Year</th>
                <th>Former Role</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(alum, idx) in activeRoleView.alumni" :key="idx">
                <td class="fw-semibold">{{ alum.name }}</td>
                <td>{{ alum.roll }}</td>
                <td>{{ alum.branch }}</td>
                <td>{{ alum.passoutYear }}</td>
                <td><span class="badge bg-secondary">{{ alum.formerRole }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- MODALS: USER PROFILE, EVENT DETAILS DASHBOARD, ASSIGN ROLE, REJECT   -->
      <!-- ==================================================================== -->

      <!-- 👤 User Profile Modal -->
      <div v-if="showUserProfileModal && selectedUserProfile" class="modal-backdrop" @click.self="showUserProfileModal = false">
        <div class="modal-dialog-custom">
          <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
            <div class="d-flex align-items-center gap-3">
              <div class="profile-avatar-large">👤</div>
              <div>
                <h4 class="m-0 fw-bold text-dark">{{ selectedUserProfile.name }}</h4>
                <span class="badge bg-primary px-2 py-1 mt-1">{{ selectedUserProfile.role }}</span>
              </div>
            </div>
            <button class="close-btn" @click="showUserProfileModal = false">&times;</button>
          </div>

          <div class="row g-3">
            <div class="col-6">
              <div class="info-box">
                <label>Roll / Reg Number</label>
                <p>{{ selectedUserProfile.roll }}</p>
              </div>
            </div>
            <div class="col-6">
              <div class="info-box">
                <label>Department / Branch</label>
                <p>{{ selectedUserProfile.branch }}</p>
              </div>
            </div>
            <div class="col-6">
              <div class="info-box">
                <label>Campus Email</label>
                <p>{{ selectedUserProfile.email }}</p>
              </div>
            </div>
            <div class="col-6">
              <div class="info-box">
                <label>Contact Phone</label>
                <p>{{ selectedUserProfile.phone }}</p>
              </div>
            </div>
            <div class="col-6">
              <div class="info-box">
                <label>Club Joining Date</label>
                <p>{{ selectedUserProfile.joinDate }}</p>
              </div>
            </div>
            <div class="col-6">
              <div class="info-box">
                <label>Events Attended</label>
                <p>{{ selectedUserProfile.eventsAttended }} Events</p>
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-end mt-4">
            <button class="btn btn-secondary" @click="showUserProfileModal = false">Close Profile</button>
          </div>
        </div>
      </div>

      <!-- 📅 EVENT DETAILS DASHBOARD MODAL (4 Sub-Tabs: Schedule, Announcements, Registrations, Attendance) -->
      <div v-if="showEventDetailsModal && selectedEventDetails" class="modal-backdrop" @click.self="showEventDetailsModal = false">
        <div class="modal-dialog-custom modal-lg-custom">
          <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
            <div>
              <span class="badge bg-primary me-2">{{ selectedEventDetails.club }}</span>
              <span class="badge" :class="selectedEventDetails.status === 'Active' ? 'bg-success' : 'bg-secondary'">
                {{ selectedEventDetails.status }}
              </span>
              <h4 class="m-0 fw-bold mt-1 text-dark">{{ selectedEventDetails.title }}</h4>
            </div>
            <button class="close-btn" @click="showEventDetailsModal = false">&times;</button>
          </div>

          <!-- Event Details Tabs -->
          <div class="detail-tabs mb-3">
            <button class="tab-option" :class="{ active: activeEventTabInModal === 'schedule' }" @click="activeEventTabInModal = 'schedule'">🗓️ Schedule</button>
            <button class="tab-option" :class="{ active: activeEventTabInModal === 'announcements' }" @click="activeEventTabInModal = 'announcements'">📢 Announcements</button>
            <button class="tab-option" :class="{ active: activeEventTabInModal === 'registrations' }" @click="activeEventTabInModal = 'registrations'">📝 Registrations</button>
            <button class="tab-option" :class="{ active: activeEventTabInModal === 'attendance' }" @click="activeEventTabInModal = 'attendance'">✅ Attendance</button>
          </div>

          <!-- Tab 1: Schedule -->
          <div v-if="activeEventTabInModal === 'schedule'">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="fw-bold m-0">Event Timeline & Agenda</h6>
              <button class="btn btn-sm btn-outline-primary" @click="showAddScheduleModal = true">+ Create Schedule</button>
            </div>
            <div v-if="selectedEventDetails.schedule.length === 0" class="text-secondary text-center py-3">No schedule added yet.</div>
            <div v-else class="schedule-list">
              <div v-for="(item, idx) in selectedEventDetails.schedule" :key="idx" class="schedule-row">
                <span class="time">{{ item.time }}</span>
                <span class="activity">{{ item.activity }}</span>
              </div>
            </div>
          </div>

          <!-- Tab 2: Announcements -->
          <div v-if="activeEventTabInModal === 'announcements'">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="fw-bold m-0">Broadcast Announcements</h6>
              <button class="btn btn-sm btn-success" @click="showAddAnnouncementModal = true">+ Trigger Announcement</button>
            </div>
            <div v-if="selectedEventDetails.announcements.length === 0" class="text-secondary text-center py-3">No announcements yet.</div>
            <div v-for="ann in selectedEventDetails.announcements" :key="ann.id" class="p-2 border-bottom">
              <div class="d-flex justify-content-between">
                <h6 class="fw-bold m-0">{{ ann.title }}</h6>
                <small class="text-secondary">{{ ann.date }}</small>
              </div>
              <p class="m-0 mt-1 text-secondary text-sm">{{ ann.message }}</p>
            </div>
          </div>

          <!-- Tab 3: Registrations -->
          <div v-if="activeEventTabInModal === 'registrations'">
            <h6 class="fw-bold mb-3">Registered Participants / Teams</h6>
            <div v-if="selectedEventDetails.registrations.length === 0" class="text-secondary text-center py-3">No registrations yet.</div>
            <table v-else class="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Participant Name</th>
                  <th>Register No</th>
                  <th>Branch</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(reg, idx) in selectedEventDetails.registrations" :key="idx">
                  <td>{{ reg.name }}</td>
                  <td>{{ reg.registerNumber }}</td>
                  <td>{{ reg.branch }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Tab 4: Attendance -->
          <div v-if="activeEventTabInModal === 'attendance'">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="fw-bold m-0">Mark Attendance</h6>
              <button class="btn btn-sm btn-primary" @click="postAttendanceInModal">Post Attendance</button>
            </div>
            <div v-if="selectedEventDetails.attendance.length === 0" class="text-secondary text-center py-3">No attendance records yet.</div>
            <table v-else class="table align-middle">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Register Number</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(att, idx) in selectedEventDetails.attendance" :key="idx">
                  <td>{{ att.name }}</td>
                  <td>{{ att.registerNumber }}</td>
                  <td>
                    <input type="checkbox" v-model="att.present" class="form-check-input me-2" />
                    <span class="badge" :class="att.present ? 'bg-success' : 'bg-danger'">
                      {{ att.present ? 'Present' : 'Absent' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="d-flex justify-content-end mt-4">
            <button class="btn btn-secondary" @click="showEventDetailsModal = false">Close</button>
          </div>
        </div>
      </div>

      <!-- Add Agenda Item Modal -->
      <div v-if="showAddScheduleModal" class="modal-backdrop" @click.self="showAddScheduleModal = false">
        <div class="modal-dialog-custom">
          <h5 class="fw-bold mb-3">+ Create Schedule Item</h5>
          <div class="mb-3">
            <label class="form-label">Time</label>
            <input v-model="newScheduleTime" type="text" class="form-control" placeholder="e.g. 10:00 AM" />
          </div>
          <div class="mb-3">
            <label class="form-label">Activity</label>
            <input v-model="newScheduleActivity" type="text" class="form-control" placeholder="e.g. Opening Keynote" />
          </div>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary" @click="showAddScheduleModal = false">Cancel</button>
            <button class="btn btn-primary" @click="addScheduleItem">Add</button>
          </div>
        </div>
      </div>

      <!-- Add Announcement Modal -->
      <div v-if="showAddAnnouncementModal" class="modal-backdrop" @click.self="showAddAnnouncementModal = false">
        <div class="modal-dialog-custom">
          <h5 class="fw-bold mb-3">+ Trigger Announcement</h5>
          <div class="mb-3">
            <label class="form-label">Title</label>
            <input v-model="newAnnouncementTitle" type="text" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Target</label>
            <select v-model="newAnnouncementTarget" class="form-select">
              <option value="Students">Students</option>
              <option value="Users">Users</option>
              <option value="All">All</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Message</label>
            <textarea v-model="newAnnouncementMessage" class="form-control" rows="3"></textarea>
          </div>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary" @click="showAddAnnouncementModal = false">Cancel</button>
            <button class="btn btn-success" @click="addAnnouncementItem">+ Trigger</button>
          </div>
        </div>
      </div>

      <!-- 🔑 Assign Role Modal -->
      <div v-if="showAssignRoleModal && selectedStudentForAssign" class="modal-backdrop" @click.self="showAssignRoleModal = false">
        <div class="modal-dialog-custom">
          <h4 class="fw-bold text-success mb-2">Assign Student Role</h4>
          <p class="text-secondary text-sm mb-3">Assigning role for <strong>{{ selectedStudentForAssign.name }}</strong> ({{ selectedStudentForAssign.roll }})</p>

          <div class="mb-3">
            <label class="form-label font-semibold">Role Title</label>
            <input v-model="assignRoleInput" type="text" class="form-control" placeholder="e.g. Club Organizer, Event Volunteer, Tech Lead" />
          </div>

          <div class="mb-3">
            <label class="form-label font-semibold">Role Description</label>
            <textarea v-model="assignRoleDescInput" class="form-control" rows="3" placeholder="Enter role responsibilities..."></textarea>
          </div>

          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary" @click="showAssignRoleModal = false">Cancel</button>
            <button class="btn btn-success" @click="confirmAssignRole">Assign Role</button>
          </div>
        </div>
      </div>

      <!-- Reject Request Modal -->
      <div v-if="showRejectModal && selectedRequestForReject" class="modal-backdrop" @click.self="showRejectModal = false">
        <div class="modal-dialog-custom">
          <h4 class="fw-bold text-danger mb-2">Reject Request</h4>
          <p class="text-secondary text-sm mb-3">Rejecting request from <strong>{{ selectedRequestForReject.studentName }}</strong></p>

          <div class="mb-3">
            <label class="form-label font-semibold">Reason for Rejection</label>
            <textarea v-model="rejectionReason" class="form-control" rows="3" placeholder="State reason for rejecting request..."></textarea>
          </div>

          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary" @click="showRejectModal = false">Cancel</button>
            <button class="btn btn-danger" @click="confirmRejectRequest">Confirm Rejection</button>
          </div>
        </div>
      </div>
    </section>
  </FacultyLayout>
</template>

<style scoped>
.roles-page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
  gap: 20px;
}

.page-header h2 {
  margin: 0;
  color: #1e293b;
  font-size: 1.75rem;
  font-weight: 700;
}

.page-header p {
  margin: 7px 0 0;
  color: #64748b;
  font-size: 0.95rem;
}

.header-actions {
  display: flex;
  gap: 14px;
}

.request-btn {
  padding: 12px 22px;
  background: #fff;
  border: 2px solid #22c55e;
  color: #22c55e;
  border-radius: 14px;
  font-weight: 600;
}

.notification-btn {
  padding: 12px 22px;
  background: #fff;
  border: 2px solid #2563eb;
  color: #2563eb;
  border-radius: 14px;
  font-weight: 600;
}

.role-card {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.role-card-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.role-icon {
  width: 52px;
  height: 52px;
  background: #f1f5f9;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
}

.role-badge {
  display: inline-block;
  background: #f0fdf4;
  color: #16a34a;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 999px;
  margin-bottom: 4px;
}

.role-title {
  margin: 0;
  color: #1e293b;
  font-weight: 700;
}

.role-description {
  color: #475569;
  font-size: 0.92rem;
  margin: 16px 0;
  flex: 1;
}

.role-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f1f5f9;
  padding-top: 16px;
}

.manage-btn {
  padding: 8px 20px;
  background: #16a34a;
  border: none;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
}

.dashboard-banner {
  background: #fff;
  border-radius: 20px;
  padding: 20px 24px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.05);
}

.back-btn {
  background: #f1f5f9;
  border: none;
  padding: 8px 14px;
  border-radius: 10px;
  color: #475569;
  font-weight: 600;
}

.banner-emoji {
  font-size: 2rem;
}

.detail-tabs {
  display: flex;
  gap: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 6px;
}

.tab-option {
  flex: 1;
  border: none;
  background: transparent;
  padding: 12px;
  border-radius: 10px;
  font-weight: 600;
  transition: 0.2s;
}

.tab-option.active {
  background: #16a34a;
  color: white;
}

.info-box {
  background: #f8fafc;
  border: 1px solid #edf2f7;
  border-radius: 14px;
  padding: 16px 20px;
}

.info-box label {
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 600;
}

.info-box p {
  margin: 4px 0 0;
  font-weight: 500;
}

.event-card-item {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.event-card-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08) !important;
}

.profile-avatar-large {
  width: 54px;
  height: 54px;
  background: #eff6ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
}

.schedule-row {
  display: flex;
  gap: 20px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.schedule-row .time {
  color: #2563eb;
  font-weight: 600;
  min-width: 90px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #94a3b8;
  cursor: pointer;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-dialog-custom {
  background: #fff;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-lg-custom {
  max-width: 750px;
}
</style>
