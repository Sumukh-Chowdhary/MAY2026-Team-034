<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import StudentLayout from '@/layouts/StudentLayout.vue'

const router = useRouter()

function navigateToEventDetails(eventId) {
  router.push(`/student/events/${eventId}`)
}

// Student's assigned roles
const assignedRoles = ref([
  {
    id: 1,
    roleName: 'Club Organizer',
    entityName: 'Music Club',
    type: 'Club',
    emoji: '🎵',
    assignedDate: '15 Jan 2026',
    facultyCoordinator: 'Dr. Ramesh Kumar',
    totalMembers: 34,
    description: 'Responsible for organizing club events, member registrations, and internal announcements.',
    members: [
      { id: 1, name: 'Rahul Sharma', roll: 'CS21B001', branch: 'CSE', joinDate: '10 Aug 2025' },
      { id: 2, name: 'Ananya Roy', roll: 'EE21B014', branch: 'EEE', joinDate: '12 Sep 2025' },
      { id: 3, name: 'Siddharth V', roll: 'ME21B033', branch: 'ME', joinDate: '01 Nov 2025' }
    ],
    joinRequests: [
      { id: 101, studentName: 'Vikas Gupta', roll: 'EC23B009', branch: 'ECE', requestDate: '18 Jul 2026' }
    ],
    events: [
      { id: 201, title: 'Annual Campus Music Fest', status: 'Active', date: '05 Aug 2026' },
      { id: 202, title: 'Acoustic Night', status: 'Completed', date: '12 Jun 2026' }
    ]
  },
  {
    id: 2,
    roleName: 'Event Volunteer',
    entityName: 'AI & Machine Learning Workshop',
    type: 'Event',
    emoji: '🤖',
    assignedDate: '10 Feb 2026',
    clubName: 'AI Club',
    status: 'Active',
    startDate: '25 Jul 2026',
    endDate: '27 Jul 2026',
    description: 'Assisting in logistics, participant check-ins, venue coordination, and attendance tracking.',
    schedule: [
      { time: '09:30 AM', activity: 'Inaugural Keynote & Orientation' },
      { time: '11:00 AM', activity: 'Hands-on PyTorch Session' },
      { time: '02:00 PM', activity: 'Model Deployment Lab' }
    ],
    announcements: [
      { id: 1, title: 'Venue Changed to Hall B', date: '20 Jul 2026', message: 'Please note the workshop will now take place in Seminar Hall B.', target: 'All' }
    ],
    registrations: [
      { name: 'Kavya Singh', registerNumber: '21B0012', branch: 'CSE' },
      { name: 'Rohan Verma', registerNumber: '21B0045', branch: 'ECE' },
      { name: 'Meera Das', registerNumber: '22B0089', branch: 'EEE' }
    ],
    attendance: [
      { name: 'Kavya Singh', registerNumber: '21B0012', present: true },
      { name: 'Rohan Verma', registerNumber: '21B0045', present: true },
      { name: 'Meera Das', registerNumber: '22B0089', present: false }
    ],
    volunteerRequests: [
      { id: 301, studentName: 'Aditya Sen', roll: 'CS23B044', message: 'Interested in assisting setup' }
    ]
  }
])

// Modal & Navigation States
const activeRoleView = ref(null) // Role being inspected
const activeClubTab = ref('details') // 'details', 'members', 'events'
const activeEventTab = ref('schedule') // 'schedule', 'announcements', 'registrations', 'attendance'

// Modal controls
const showCreateEventModal = ref(false)
const showCreateScheduleModal = ref(false)
const showCreateAnnouncementModal = ref(false)

// Forms
const newEventForm = ref({ title: '', startDate: '', endDate: '', permissionsTag: '', description: '' })
const newScheduleForm = ref({ time: '', activity: '' })
const newAnnouncementForm = ref({ title: '', target: 'All', message: '' })

function openRoleDashboard(role) {
  activeRoleView.value = JSON.parse(JSON.stringify(role))
  if (role.type === 'Club') activeClubTab.value = 'details'
  if (role.type === 'Event') activeEventTab.value = 'schedule'
}

function closeDashboard() {
  activeRoleView.value = null
}

function handleLeaveRole(roleId) {
  if (confirm('Are you sure you want to step down from this role?')) {
    assignedRoles.value = assignedRoles.value.filter((r) => r.id !== roleId)
    closeDashboard()
  }
}

// Club Event Creation
function submitNewEvent() {
  if (!newEventForm.value.title.trim()) return alert('Please enter an Event Name')
  activeRoleView.value.events.push({
    id: Date.now(),
    title: newEventForm.value.title,
    status: 'Active',
    date: newEventForm.value.startDate || 'TBD'
  })
  alert('Event proposal created successfully!')
  showCreateEventModal.value = false
  newEventForm.value = { title: '', startDate: '', endDate: '', permissionsTag: '', description: '' }
}

// Volunteer Event Agenda / Schedule Creation
function submitNewSchedule() {
  if (!newScheduleForm.value.activity.trim()) return alert('Please enter activity')
  activeRoleView.value.schedule.push({
    time: newScheduleForm.value.time || '10:00 AM',
    activity: newScheduleForm.value.activity
  })
  showCreateScheduleModal.value = false
  newScheduleForm.value = { time: '', activity: '' }
}

// Volunteer Announcement Trigger
function submitNewAnnouncement() {
  if (!newAnnouncementForm.value.title.trim()) return alert('Please enter title')
  activeRoleView.value.announcements.unshift({
    id: Date.now(),
    title: newAnnouncementForm.value.title,
    target: newAnnouncementForm.value.target,
    message: newAnnouncementForm.value.message,
    date: new Date().toLocaleDateString()
  })
  alert(`Announcement triggered for ${newAnnouncementForm.value.target}! Notifications sent.`)
  showCreateAnnouncementModal.value = false
  newAnnouncementForm.value = { title: '', target: 'All', message: '' }
}

// Attendance Checkbox & Post
function postAttendance() {
  const presentCount = activeRoleView.value.attendance.filter(a => a.present).length
  const totalCount = activeRoleView.value.attendance.length
  alert(`Attendance posted! ${presentCount}/${totalCount} students marked present.`)
}
</script>

<template>
  <StudentLayout>
    <section class="roles-page">
      <!-- Header -->
      <div class="page-header">
        <div>
          <h2>My Roles</h2>
          <p>View your assigned club and event management roles.</p>
        </div>
      </div>

      <!-- State A: Empty State (When student holds no roles) -->
      <div v-if="assignedRoles.length === 0" class="empty-state-card">
        <div class="empty-icon">🛡️</div>
        <h3>You are not Assigned to any roles</h3>
        <p>If you are not an Organizer for any Event or for any Club, your active roles dashboard will appear empty. Join clubs or apply for volunteering to get assigned!</p>
      </div>

      <!-- State B: Active Roles Grid (Club Organizer / Event Volunteer) -->
      <div v-else-if="!activeRoleView" class="row g-4">
        <div
          v-for="role in assignedRoles"
          :key="role.id"
          class="col-12 col-md-6"
        >
          <div class="role-card">
            <div class="role-card-header">
              <div class="role-icon">{{ role.emoji }}</div>
              <div>
                <span class="role-type-badge" :class="role.type.toLowerCase()">{{ role.roleName }}</span>
                <h5 class="role-title">{{ role.entityName }}</h5>
                <span class="assigned-date">Assigned: {{ role.assignedDate }}</span>
              </div>
            </div>

            <p class="role-description">{{ role.description }}</p>

            <div class="role-card-footer">
              <span class="text-secondary text-sm">Role Type: {{ role.type }}</span>
              <button class="view-btn" @click="openRoleDashboard(role)">
                View Management Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- UNLOCKED DASHBOARD VIEW: CLUB ORGANIZER / EVENT VOLUNTEER            -->
      <!-- ==================================================================== -->
      <div v-if="activeRoleView" class="unlocked-dashboard">
        <!-- Dashboard Sub-Header -->
        <div class="dashboard-banner mb-4">
          <div class="d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-3">
              <button class="back-btn" @click="closeDashboard">← Back to Roles</button>
              <div class="banner-emoji">{{ activeRoleView.emoji }}</div>
              <div>
                <h3 class="m-0 text-dark font-bold">{{ activeRoleView.entityName }}</h3>
                <span class="badge bg-primary px-3 py-1 mt-1">{{ activeRoleView.roleName }}</span>
              </div>
            </div>

            <button class="btn btn-outline-danger" @click="handleLeaveRole(activeRoleView.id)">
              Leave Role
            </button>
          </div>
        </div>

        <!-- ------------------------------------------------------------------ -->
        <!-- A. CLUB ORGANIZER DASHBOARD (3 TABS: Details, Members, Events)     -->
        <!-- ------------------------------------------------------------------ -->
        <div v-if="activeRoleView.type === 'Club'">
          <!-- Navigation Tabs -->
          <div class="detail-tabs mb-4">
            <button
              class="tab-option"
              :class="{ active: activeClubTab === 'details' }"
              @click="activeClubTab = 'details'"
            >
              📌 Details
            </button>
            <button
              class="tab-option"
              :class="{ active: activeClubTab === 'members' }"
              @click="activeClubTab = 'members'"
            >
              👥 Members & Requests
            </button>
            <button
              class="tab-option"
              :class="{ active: activeClubTab === 'events' }"
              @click="activeClubTab = 'events'"
            >
              📅 Club Events
            </button>
          </div>

          <!-- Tab 1: Details -->
          <div v-if="activeClubTab === 'details'" class="card p-4 shadow-sm border-0 rounded-4">
            <h5 class="fw-bold mb-3">Club Details</h5>
            <div class="row g-3">
              <div class="col-md-6">
                <div class="info-box">
                  <label>Faculty Coordinator</label>
                  <p>{{ activeRoleView.facultyCoordinator }}</p>
                </div>
              </div>
              <div class="col-md-6">
                <div class="info-box">
                  <label>Total Enrolled Members</label>
                  <p>{{ activeRoleView.totalMembers }} Members</p>
                </div>
              </div>
              <div class="col-12">
                <div class="info-box">
                  <label>Club Description</label>
                  <p>{{ activeRoleView.description }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Tab 2: Members (With Join Requests, 🔒 No Assign/Remove buttons) -->
          <div v-if="activeClubTab === 'members'" class="card p-4 shadow-sm border-0 rounded-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-bold m-0">Enrolled Members</h5>
              <span class="text-secondary text-sm">🔒 Role assignment/removal is managed by Faculty</span>
            </div>

            <!-- Member Roster Table -->
            <table class="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Roll Number</th>
                  <th>Branch</th>
                  <th>Joined Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in activeRoleView.members" :key="m.id">
                  <td class="fw-semibold">{{ m.name }}</td>
                  <td>{{ m.roll }}</td>
                  <td>{{ m.branch }}</td>
                  <td>{{ m.joinDate }}</td>
                </tr>
              </tbody>
            </table>

            <!-- Pending Join Requests Section -->
            <div class="mt-4 pt-3 border-top">
              <h6 class="fw-bold mb-3">Pending Join Requests (`Member Request`)</h6>
              <div v-if="activeRoleView.joinRequests.length === 0" class="text-secondary">No pending requests.</div>
              <div v-else class="row g-3">
                <div v-for="req in activeRoleView.joinRequests" :key="req.id" class="col-md-6">
                  <div class="p-3 border rounded-3 bg-light d-flex justify-content-between align-items-center">
                    <div>
                      <h6 class="m-0 fw-bold">{{ req.studentName }}</h6>
                      <small class="text-secondary">{{ req.roll }} · {{ req.branch }}</small>
                    </div>
                    <span class="badge bg-warning text-dark">Pending Review</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Tab 3: Events (+ Create Event Form) -->
          <div v-if="activeClubTab === 'events'" class="card p-4 shadow-sm border-0 rounded-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="fw-bold m-0">Club Events</h5>
              <button class="btn btn-primary" @click="showCreateEventModal = true">+ Create Event</button>
            </div>

            <div class="row g-3">
              <div v-for="ev in activeRoleView.events" :key="ev.id" class="col-md-6">
                <div class="p-3 border rounded-3 bg-white d-flex justify-content-between align-items-center cursor-pointer shadow-sm" @click="navigateToEventDetails(ev.id)">
                  <div>
                    <h6 class="m-0 fw-bold text-primary">{{ ev.title }}</h6>
                    <small class="text-secondary">Date: {{ ev.date }}</small>
                  </div>
                  <div class="d-flex align-items-center gap-2">
                    <span class="badge" :class="ev.status === 'Active' ? 'bg-success' : 'bg-secondary'">{{ ev.status }}</span>
                    <button class="btn btn-sm btn-outline-primary py-0 px-2">View →</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ------------------------------------------------------------------ -->
        <!-- B. EVENT VOLUNTEER DASHBOARD (4 TABS: Schedule, Announcements, etc)-->
        <!-- ------------------------------------------------------------------ -->
        <div v-if="activeRoleView.type === 'Event'">
          <!-- Navigation Tabs -->
          <div class="detail-tabs mb-4">
            <button
              class="tab-option"
              :class="{ active: activeEventTab === 'schedule' }"
              @click="activeEventTab = 'schedule'"
            >
              🗓️ Schedule
            </button>
            <button
              class="tab-option"
              :class="{ active: activeEventTab === 'announcements' }"
              @click="activeEventTab = 'announcements'"
            >
              📢 Announcements
            </button>
            <button
              class="tab-option"
              :class="{ active: activeEventTab === 'registrations' }"
              @click="activeEventTab = 'registrations'"
            >
              📝 Registrations
            </button>
            <button
              class="tab-option"
              :class="{ active: activeEventTab === 'attendance' }"
              @click="activeEventTab = 'attendance'"
            >
              ✅ Attendance
            </button>
          </div>

          <!-- Sub-Tab 1: Schedule -->
          <div v-if="activeEventTab === 'schedule'" class="card p-4 shadow-sm border-0 rounded-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-bold m-0">Event Schedule & Agenda</h5>
              <button class="btn btn-sm btn-outline-primary" @click="showCreateScheduleModal = true">+ Add Agenda</button>
            </div>

            <div class="schedule-list">
              <div v-for="(item, idx) in activeRoleView.schedule" :key="idx" class="schedule-row">
                <span class="time">{{ item.time }}</span>
                <span class="activity">{{ item.activity }}</span>
              </div>
            </div>
          </div>

          <!-- Sub-Tab 2: Announcements -->
          <div v-if="activeEventTab === 'announcements'" class="card p-4 shadow-sm border-0 rounded-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-bold m-0">Announcements</h5>
              <button class="btn btn-sm btn-success" @click="showCreateAnnouncementModal = true">+ Trigger Announcement</button>
            </div>

            <div v-for="ann in activeRoleView.announcements" :key="ann.id" class="p-3 border-bottom">
              <div class="d-flex justify-content-between">
                <h6 class="fw-bold m-0">{{ ann.title }}</h6>
                <small class="text-secondary">{{ ann.date }}</small>
              </div>
              <p class="m-0 mt-2 text-secondary">{{ ann.message }}</p>
              <span class="badge bg-light text-primary border mt-2">Target: {{ ann.target }}</span>
            </div>
          </div>

          <!-- Sub-Tab 3: Registrations -->
          <div v-if="activeEventTab === 'registrations'" class="card p-4 shadow-sm border-0 rounded-4">
            <h5 class="fw-bold mb-3">Registered Participants</h5>
            <table class="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Participant Name</th>
                  <th>Register Number</th>
                  <th>Branch</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(reg, idx) in activeRoleView.registrations" :key="idx">
                  <td class="fw-semibold">{{ reg.name }}</td>
                  <td>{{ reg.registerNumber }}</td>
                  <td>{{ reg.branch }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Sub-Tab 4: Attendance Marking -->
          <div v-if="activeEventTab === 'attendance'" class="card p-4 shadow-sm border-0 rounded-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 class="fw-bold m-0">Participant Attendance</h5>
                <span class="text-secondary text-sm">
                  Present Ratio: {{ activeRoleView.attendance.filter(a=>a.present).length }} / {{ activeRoleView.attendance.length }}
                </span>
              </div>
              <button class="btn btn-primary" @click="postAttendance">Post Attendance</button>
            </div>

            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Participant Name</th>
                  <th>Register Number</th>
                  <th>Mark Present</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(att, idx) in activeRoleView.attendance" :key="idx">
                  <td>{{ att.name }}</td>
                  <td>{{ att.registerNumber }}</td>
                  <td>
                    <input type="checkbox" v-model="att.present" class="form-check-input ms-2" />
                    <span class="ms-2 badge" :class="att.present ? 'bg-success' : 'bg-danger'">
                      {{ att.present ? 'Present' : 'Absent' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- MODALS FOR EVENT / SCHEDULE / ANNOUNCEMENT CREATION                   -->
      <!-- ==================================================================== -->

      <!-- Create Event Modal -->
      <div v-if="showCreateEventModal" class="modal-backdrop" @click.self="showCreateEventModal = false">
        <div class="modal-dialog-custom">
          <h4 class="fw-bold mb-3">+ Create Event</h4>
          <div class="mb-3">
            <label class="form-label">Event Name</label>
            <input v-model="newEventForm.title" type="text" class="form-control" placeholder="Enter event title" />
          </div>
          <div class="row g-2 mb-3">
            <div class="col-6">
              <label class="form-label">Start Date</label>
              <input v-model="newEventForm.startDate" type="date" class="form-control" />
            </div>
            <div class="col-6">
              <label class="form-label">End Date</label>
              <input v-model="newEventForm.endDate" type="date" class="form-control" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Tag all Users for Permissions</label>
            <input v-model="newEventForm.permissionsTag" type="text" class="form-control" placeholder="e.g. @all, @organizers" />
          </div>
          <div class="mb-3">
            <label class="form-label">Description</label>
            <textarea v-model="newEventForm.description" class="form-control" rows="3"></textarea>
          </div>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary" @click="showCreateEventModal = false">Cancel</button>
            <button class="btn btn-success" @click="submitNewEvent">Send Proposal</button>
          </div>
        </div>
      </div>

      <!-- Create Schedule Modal -->
      <div v-if="showCreateScheduleModal" class="modal-backdrop" @click.self="showCreateScheduleModal = false">
        <div class="modal-dialog-custom">
          <h4 class="fw-bold mb-3">+ Create Agenda Item</h4>
          <div class="mb-3">
            <label class="form-label">Time</label>
            <input v-model="newScheduleForm.time" type="text" class="form-control" placeholder="e.g. 10:30 AM" />
          </div>
          <div class="mb-3">
            <label class="form-label">Activity Description</label>
            <input v-model="newScheduleForm.activity" type="text" class="form-control" placeholder="e.g. Welcome Address" />
          </div>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary" @click="showCreateScheduleModal = false">Cancel</button>
            <button class="btn btn-primary" @click="submitNewSchedule">Add Agenda</button>
          </div>
        </div>
      </div>

      <!-- Create Announcement Modal -->
      <div v-if="showCreateAnnouncementModal" class="modal-backdrop" @click.self="showCreateAnnouncementModal = false">
        <div class="modal-dialog-custom">
          <h4 class="fw-bold mb-3">+ Trigger Announcement</h4>
          <div class="mb-3">
            <label class="form-label">Announcement Title</label>
            <input v-model="newAnnouncementForm.title" type="text" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Target Audience</label>
            <select v-model="newAnnouncementForm.target" class="form-select">
              <option value="Students">Students</option>
              <option value="Users">Users</option>
              <option value="All">All</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Message</label>
            <textarea v-model="newAnnouncementForm.message" class="form-control" rows="3"></textarea>
          </div>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary" @click="showCreateAnnouncementModal = false">Cancel</button>
            <button class="btn btn-success" @click="submitNewAnnouncement">+ Trigger</button>
          </div>
        </div>
      </div>
    </section>
  </StudentLayout>
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

.empty-state-card {
  background: #fff;
  border-radius: 20px;
  padding: 60px 30px;
  text-align: center;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.05);
}

.empty-icon {
  font-size: 3.5rem;
  margin-bottom: 16px;
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

.role-type-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 999px;
  margin-bottom: 4px;
  background: #eff6ff;
  color: #2563eb;
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

.view-btn {
  padding: 8px 20px;
  background: #eff6ff;
  border: none;
  border-radius: 10px;
  color: #2563eb;
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
  background: #2563eb;
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

.schedule-row {
  display: flex;
  gap: 20px;
  padding: 14px 0;
  border-bottom: 1px solid #f1f5f9;
}

.schedule-row .time {
  color: #2563eb;
  font-weight: 600;
  min-width: 90px;
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
</style>
